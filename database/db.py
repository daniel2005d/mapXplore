from connection import Connection
from utils.utils import Hashing
from config.settings import Settings

class DataBase:
    def __init__(self, dbname:str, connectionsettings:Connection):
            if connectionsettings is not None:
                self.username = connectionsettings.username
                self.password = connectionsettings.password
                self.host = connectionsettings.server

            self._database = dbname
            self._status_handler = None
            self._hashcolumn = Settings.checksum_column
            self._recreate = Settings.setting["Database"]["recreate"]
            self._tables = []
    
    @property
    def principal_database(self)->str:
        pass
    
    @property
    def recreate(self) -> bool:
        return self._recreate
    
    @recreate.setter
    def recreate(self, value:bool):
        Settings.setting["Database"]["recreate"]=value

    @property
    def status_handler(self):
        return self._status_handler

    @status_handler.setter
    def status_handler(self, value):
        self._status_handler = value

    def _get_columns(self, tablename:str):
        pass

    def _get_columns_from_table(self, tablename:str):
        pass
    """
    Check if Table exists
    """
    def check_exists_table(self, tablename:str) -> bool:
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    """
    If database exists, drop and create
    """
    def create_database(self, dbname:str):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")
    
    def create_table(self, name:str, columns=None):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    def create_columns(self, tablename:str, columns):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")
  
    def insert_data(self, tablename, data, columns=None):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    def insert_many(self, tablename, data, columns=None):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")
    
    def search_tables(self, filter:str):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    def search_columns(self, filter:str):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    def get_tables_and_columns(self):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    """
    Retrieve all tables and columns to try find out
    information inside this
    """
    def create_query_to_all_values(self, value_to_find, operator='or'):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    def execute_query(self, query:str):
        raise ModuleNotFoundError(f"{str(self)} Not implemented")

    def test_connection(self):
        pass

    def _gethash(self, data):
        line = ''.join(data)
        return Hashing.get_md5(line)


