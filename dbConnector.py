from database.connection import Connection
from database.PostgreSQL import PostgreSQL
from database.SQliteDB import SQLite
from middle.mapexception import MapXploreException

class DbConnector:
    def __init__(self,*argv, **kwargs) -> None:
        arguments = None
        if len(kwargs) == 0:
            arguments = argv[0]
        else:
            arguments = Connection()
            for key,value in kwargs.items():
                setattr(arguments, key, value)

        self._delimiter = arguments.delimiter if hasattr(arguments, "delimiter") else ","
        self._table= arguments.table if hasattr(arguments, "table") else None
        self._recreate = arguments.recreate if hasattr(arguments, "recreate")   else False
        self._database = arguments.database if hasattr(arguments, "database")   else None
        self._host = arguments.host
        self._username = arguments.username
        self._password = arguments.password
        self._connection = Connection(server=arguments.host,username=arguments.username,password=arguments.password)
        self._dbms = arguments.dbms
        

    def _createDBEngine(self, database=None, connection=None):
        con = None
        try:
            if database is None and self._database is not None:
                database = self._database
            
            if self._dbms == 'postgres':
                con = PostgreSQL(database.lower() if database is not None else None, self._connection if connection is None else connection)
            elif self._dbms == 'sqlite':
                con = SQLite(database, None)
            if con:
                con.test_connection()
        except Exception as e:
            raise e
        
        return con
