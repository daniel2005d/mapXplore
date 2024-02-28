from typing import List
from utils.crypto.hashes import Hashes
import os


class Settings:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def sqlmap_config(args):
        Settings.setting["sqlmap"]["input"]=args.input if args.input is not None else None
        Settings.setting["sqlmap"]["csvdelimiter"] = args.delimiter if args.delimiter is not None else ","
        Settings.setting["sqlmap"]["database"] = args.database
        Settings.setting["sqlmap"]["recreate"] = args.recreate

    special_column_names={
        "TypeTitle":"TypeFormat_{col_name}",
        "ContentTitle":"DataFromBase64_{col_name}"
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
            "elapsed":True,
            "includeb64":True
        },
        "Database":{
            "host":"30.0.1.108",
            "username":"postgres",
            "password":"3A9eQAHluSe7",
            "database":"",
            "dbms":"postgres"
        },
        "Results":{
            "output":"",
            "savefiles":False,
            "format":'csv',
            "truncate":10,
            "csvdelimiter":","
        },
        "sqlmap":{
            "input":"",
            "csvdelimiter":",",
            "database":"",
            "recreate":False
            
        }


    }


    @staticmethod
    def set_value(section, key, value):
        pass

    