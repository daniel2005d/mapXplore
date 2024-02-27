from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from config.settings import Settings


class Database():

    def __init__(self) -> None:
        self._recreate = False
        base = declarative_base()
        db_config = Settings.setting["Database"]

        username = db_config["username"]
        password = db_config["password"]
        host = db_config["host"]
        database = db_config["database"]
        connectionString = f"postgresql://{username}:{password}@{host}"
        self._engine = create_engine(connectionString, echo=True)

    
    @property
    def recreate(self):
        return self._recreate

    @recreate.setter
    def recreate(self, value:bool):
        self._recreate=value
    
    def create_database(self, name:str):
        with self._engine.connect() as connection:
            connection.execute(f"CREATE DATABASE database_name")
    


    

