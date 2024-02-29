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
            "includeb64":True,
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
            "csvdelimiter":",",
            "includedocuments":False
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
                    Settings.setting = json.load(jfile)
        except Exception as e:
            raise MapXploreException(message=str(e))

class ResultSetting:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls,*args, **kwargs)
        
        return cls._instance
        
    def __init__(self) -> None:
        self._settings = Settings.setting["Results"]
    
    
    def include_documents(self) -> bool:
        if "includedocuments" in self._settings:
            return self._settings["includedocuments"]
        
        return False