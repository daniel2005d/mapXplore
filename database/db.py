from connection import Connection
from utils import Hashing

class DataBase:
    def __init__(self, dbname:str, connectionsettings:Connection):
            self.username = connectionsettings.username
            self.password = connectionsettings.password
            self.host = connectionsettings.server
            self._database = dbname
            self._status_handler = None
            self._hashcolumn = "sqlmap_hash"
            self._recreate = True
            self._tables = []
    
    @property
    def recreate(self) -> bool:
        return self._recreate
    
    @recreate.setter
    def recreate(self, value:bool):
        self._recreate = value

    @property
    def status_handler(self):
        return self._status_handler

    @status_handler.setter
    def status_handler(self, value):
        self._status_handler = value

    """
    Check if Table exists
    """
    def check_exists_table(self, tablename:str) -> bool:
        pass

    """
    If database exists, drop and create
    """
    def create_database(self, dbname:str):
        pass
    
    def create_table(self, name:str, columns=None):
        pass

    def create_columns(self, tablename:str, columns):
        pass
  
    def insert_data(self, tablename, data, columns=None):
        pass

    def search_tables(self, filter:str):
        pass

    def search_columns(self, filter:str):
        pass

    def _get_columns(self, tablename:str):
        pass

    def _get_columns_from_table(self, tablename:str):
        pass

    def get_tables_and_columns(self):
        pass

    def create_query_to_all_values(self, value_to_find, operator='or'):
        pass

    def execute_query(self, query:str):
        pass

    def _gethash(self, data):
        line = ''.join(data)
        return Hashing.get_md5(line)


