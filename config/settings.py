import os
import json
from typing import List
from lib.crypto.hashes import Hashes
from utils.utils import Util
from middle.mapexception import MapXploreException
import i18n.locale as locale
from enum import Enum


class Settings:
    
    COMMAND_PREFIX = "do_"
   
    folder_by_extension = {
        'pdf':['pdf'],
        'documents':['docx','xlsx','pptx','ppt','doc','xls'],
        'images':['png','jpg','jpeg','gif'],
        'text':['txt']
    }
    
    special_column_names={
        "TypeTitle":"TypeFormat_{col_name}",
        "ContentTitle":"DataFromBase64_{col_name}"
    }

    principal_databases:dict={
        'postgres':'postgres',
        'sqlite':None
    }

    _default_commands = ['set','shortcuts','shell','alias','edit','macro','run_pyscript','run_script']

    checksum_column = 'sqlmap_hash'
    valid_format_files = ['html','xlsx','json']
    exclude_data_type: List[str] = ["boolean","timestamp without time zone","date","datetime"]
    filter_options = ['tables','columns','values','all']
    allow_hashes = Hashes.get_available_algorithms()
    setting = {
        
        "General":{
            "debug":False
        },
        "Import":{
            "strict":True,
            "validchars":"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>@[\\]^_`{|}"
        },
        "Server":{
            "host":"",
            "username":"",
            "password":"",
            "dbms":"postgres"
        },
        "Results":{
            "output":"",
            "format":'xlsx'
            
        },
        "sqlmap":{
            "input":"",
            "csvdelimiter":",",
            "database":""
        }
    }

    @staticmethod
    def get_default_commands():
        formatted_comands = []
        for command in Settings._default_commands:
            formatted_comands.append(Settings.COMMAND_PREFIX+command)
        
        return formatted_comands

    @staticmethod
    def parseBool(value:str)->bool:
        return  value.lower() in ('yes','true','1','t')
    
    @staticmethod
    def set_value(section, key, value):
        if section in Settings.setting:
            if key in Settings.setting[section]:
                Settings.setting[section][key]=value if key != 'debug' else Settings.parseBool(value)
            else:
                message = locale.get("errors.section_config_error")
                raise MapXploreException(message=message.format(section=section))
        else:
            message = locale.get("errors.section_config_error")
            raise MapXploreException(message=message.format(section=section))
    
    @staticmethod
    def save_settings(filename:str, override=False)->None:
        
        try:
            filename = os.path.expanduser(filename)
            if Util.check_file(filename) and not override:
                raise MapXploreException(message_key="file_exists", isError=False)
            else:
                with open(filename, "w") as jfile:
                    json.dump(Settings.setting, jfile)
        except MapXploreException as e:
            raise e
        except Exception as e:
            raise MapXploreException(e)
    
    @staticmethod
    def load_settings(filename:str)->None:
        
        try:
            if not Util.check_file(filename):
                raise MapXploreException(message=locale.get("errors.file_not_exists").format(file=filename))
            else:
                with open(filename, "r") as jfile:
                    json_data = json.load(jfile)
                    Settings.setting.update(json_data)
        except Exception as e:
            raise MapXploreException(message=str(e))

    @staticmethod
    def get_principal_db(dbms)->str:
        return Settings.principal_databases[dbms]

class BaseSetting:
    _instance = None
    __setting_key__ = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls,*args, **kwargs)
        
        return cls._instance

    def _get_value(self, key)->str:
        setting = Settings.setting[self.__setting_key__]
        value = None
        if key in setting:
            value = setting[key]
            if not value:
                value = None
        
        return value

    def _get_bool(self, key)->bool:
        value = self._get_value(key)
        return value if value is not None else False
    
    def set_value(self, section, value):
        Settings.setting[self.__setting_key__][section]=value
    
    @property
    def keys(self):
        return Settings.setting[self.__setting_key__].keys()
    
    @property
    def key_name(self):
        return self.__setting_key__

    
class ResultSetting(BaseSetting):
    class ExportFileType(Enum):
        HTML= 0
        Excel = 1
        JSON = 2


    __setting_key__ = "Results"

    @property
    def output(self)->str:
        output_dir = self._get_value("output")
        if output_dir:
            output_dir = os.path.expanduser(output_dir)
        
        return output_dir

    @output.setter
    def output(self, value)->str:
        Settings.setting[self.__setting_key__]["output"]=value
    
    @property
    def format(self)->str:
        return self._get_value("format")
    
    @property
    def get_FileType(self) -> ExportFileType:
        if self.format.lower() == 'html':
            return ResultSetting.ExportFileType.HTML
        elif self.format.lower() == 'xlsx':
            return ResultSetting.ExportFileType.Excel
        elif self.format.lower() == 'json':
            return ResultSetting.ExportFileType.JSON
        else:
            raise MapXploreException(message_key="errors.invalid_format")
    
    def get_folder_output(self, path_to_join=None):
        database_name = ""
        if DatabaseSetting().database_name:
            database_name = DatabaseSetting().database_name
        elif SqlMapSetting().database:
            database_name = SqlMapSetting().database
        
        main_directory = os.path.expanduser(self.output)
        if path_to_join:
            return os.path.join(main_directory, database_name, path_to_join)
        else:
            return os.path.join(main_directory, database_name)

class DatabaseSetting(BaseSetting):
    __setting_key__ = "Server"
    
    @property
    def section_name(self) -> str:
        return self._key
    
    @property
    def host(self)->str:
        return self._get_value("host")
    
    @property
    def database_name(self)->str:
        sqlmap_db = SqlMapSetting().database
        return sqlmap_db.lower() if sqlmap_db is not None else None
    
    @property
    def dbms(self)->str:
        return self._get_value("dbms")
    
    @property
    def username(self)->str:
        return self._get_value("username")
    
    @property
    def password(self)->str:
        return self._get_value("password")

class GeneralSetting(BaseSetting):
    __setting_key__ = "General"

    @property
    def isDebug(self)->bool:
        return self._get_bool("debug")
    
class SqlMapSetting(BaseSetting):
    __setting_key__ = "sqlmap"


    @property
    def file_input(self)->str:
        return self._get_value("input")
    
    @property
    def csv_delimiter(self)->str:
        return self._get_value("csvdelimiter")

    @property
    def database(self)->str:
        return self._get_value("database")
    
    @database.setter
    def database(self, value)->str:
        self.set_value("database", value)
    
    def get_dump_dir(self)->str:
        dump_directory = os.path.expanduser(self.file_input)
        dump_directory = os.path.join(dump_directory, "dump")
        return dump_directory
    
    def get_files_ofDatabase(self) -> dict:
        dump_dir = self.get_dump_dir()
        files = []
        
        dump_dir = os.path.join(dump_dir, self.database)
        for name in os.listdir(dump_dir):
            if not name.startswith("."):
                path_file = os.path.join(dump_dir, name)
                if os.path.isfile(path_file):
                    ext_tmp = name.split('.')[-1:][0]
                    if ext_tmp.isdigit() or ext_tmp.lower() == 'csv':
                        files.append({"filename":name, "path":path_file})
    
        return files
    
    def get_databases(self):
        directories = []
        dump_dir = self.get_dump_dir()
        if self.database:
            directories.append(self.database)
        else:
            if os.path.exists(dump_dir):
                directories = [name for name in os.listdir(dump_dir) if os.path.isdir(os.path.join(dump_dir, name))]
                
            else:
                raise MapXploreException(message=locale.get("dir_not_not").format(directory=dump_dir))
            
        return directories

class ImportSetting(BaseSetting):
    __setting_key__ = "Import"
    #  "strict":True,
    #         "validchars":"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c"

    @property
    def isStrict(self)->bool:
        return self._get_bool("strict")

    @property
    def valid_chars(self)->list[str]:
        return list(self._get_value("validchars"))
