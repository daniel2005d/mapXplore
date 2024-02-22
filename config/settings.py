from typing import List

class Settings:
    def __init__(self) -> None:
        pass
    
    special_column_names={
        "TypeTitle":"TypeFormat_{col_name}",
        "ContentTitle":"DataFromBase64_{col_name}"
    }

    exclude_data_type: List[str] = ["boolean","timestamp without time zone","date","datetime"]
    filter_options = ['tables','columns','values','all']
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
            "truncate":10
        }

    }


    @staticmethod
    def set_value(section, key, value):
        pass

# class DatabaseSettings:
#     def __init__(self, **kwargs) -> None:
#         self._settings = {}
    
#     @property
#     def get(self):
#         return self._settings

#     @set.setter
#     def set(self, option, value):
#         self._settings[option]=value
        


    