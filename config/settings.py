from typing import List
from utils.crypto.hashes import Hashes

class Settings:
    def __init__(self) -> None:
        pass
    
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
            "elapsed":True
        },
        "Database":{
            "host":"",
            "username":"",
            "password":"",
            "database":"",
            "dbtype":""
        },
        "Results":{
            "output":"",
            "savefiles":False,
            "format":'csv',
            "truncate":10,
            "csvdelimiter":","
        }

    }


    @staticmethod
    def set_value(section, key, value):
        pass

    