from typing import List
from utils.crypto.hashes import Hashes
from utils.utils import Util
from middle.mapexception import MapXploreException
import i18n.locale as locale
import os
import json


class Settings:
    def __init__(self) -> None:
        pass
   
    special_column_names={
        "TypeTitle":"TypeFormat_{col_name}",
        "ContentTitle":"DataFromBase64_{col_name}"
    },

    principal_databases={
        'postgres':'postgres',
        'sqlite':None
    }

    checksum_column = 'sqlmap_hash'
    valid_format_files = ['html','csv','json']
    exclude_data_type: List[str] = ["boolean","timestamp without time zone","date","datetime"]
    filter_options = ['tables','columns','values','all']
    allow_hashes = Hashes.get_available_algorithms()
    setting = {
        "Query":{
            "operator":"ilike",
            "logical_operator":"or"
            
        },
        "General":{
            "debug":False
        },
        "Database":{
            "host":"",
            "username":"",
            "password":"",
            "database":"",
            "dbms":"postgres",
            "recreate":False
        },
        "Results":{
            "output":"",
            "savefiles":False,
            "format":'csv',
            "csvdelimiter":","
        },
        "sqlmap":{
            "input":"",
            "csvdelimiter":",",
            "database":""
        }
    }


    @staticmethod
    def set_value(section, key, value):
        Settings.setting[section][key]=value
    
    @staticmethod
    def save_settings(filename:str, override=False)->None:
        
        try:
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
                    Settings.setting.update(json.load(jfile))
        except Exception as e:
            raise MapXploreException(message=str(e))

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

class ResultSetting(BaseSetting):

    __setting_key__ = "Results"

    @property
    def output(self)->str:
        return self._get_value("output")

    @output.setter
    def output(self, value)->str:
        Settings.setting[self.__setting_key__]["output"]=value
    
    @property
    def save_files(self)->bool:
        return self._get_bool("savefiles")
    
    @property
    def format(self)->str:
        return self._get_value("format")
    
    @property
    def csv_delimiter(self)->str:
        return self._get_value("csvdelimiter")
    
class DatabaseSetting(BaseSetting):
    __setting_key__ = "Database"
    
    @property
    def section_name(self) -> str:
        return self._key
    
    @property
    def host(self)->str:
        return self._get_value("host")
    
    @property
    def database_name(self)->str:
        return self._get_value("database")
    
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
