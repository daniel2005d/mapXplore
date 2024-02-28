from db import DataBase
import sqlite3
from utils.savemanager import SaveManager
import os


class SQLite(DataBase):
    
    @property
    def principal_database(self)->str:
        return ""

    def _get_db_file(self):
        manager = SaveManager()
        home = os.path.expanduser("~")
        path = os.path.join(home,'.local','share','mapXplore')
        manager._create_directory(path)
        return path
    
    def _get_cursor(self, database:str=None):
        path_db = self._get_db_file()
        db_file = os.path.join(path_db, database if database is not None else self._database)
        conn = sqlite3.connect(db_file+".db")
        self._conn = conn
        return conn.cursor()

    def _execute(self, sentence, values=None):
        cursor = self._get_cursor()
        if values is not None:
            cursor.execute(sentence, values)
        else:
            cursor.execute(sentence)

        self._conn.commit()
        self._conn.close()
    
    def _select(self, sentence: str, values=None, showColumns = False):
        cursor = self._get_cursor()
        cursor.execute(sentence, values)
        rows = cursor.fetchall()
        self._conn.close()
        return rows

    def _get_columns(self, tablename:str):
        return self._get_columns_from_table(tablename)
    
    def _get_columns_from_table(self, tablename:str):
        columns = []
        cur = self._get_cursor()
        cur.execute(f"PRAGMA table_info({tablename})")
        rows = cur.fetchall()
        for row in rows:
            columns.append(row[1])
        return columns

    def _check_exists_column(self, tablename:str, column_name:str) ->bool:
        
        columns = self._get_columns_from_table(tablename)
        for col in columns:
            if col == column_name:
                self._conn.close()
                return True
        self._conn.close()
        return False

    def create_database(self, dbname:str):
        self._get_cursor(dbname)
        self._conn.close()
    
    def check_exists_table(self, tablename:str) -> bool:
        table = self._select("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tablename,))
        return len(table)>0


    def create_table(self, name:str, columns=None):
        sentence = f"CREATE TABLE IF NOT EXISTS {name} ({self._hashcolumn} varchar(50))"
        self._execute(sentence)
        if self.check_exists_table(name):
            self.create_columns(name, columns)
    
    def create_columns(self, tablename:str, columns):
        if self._hashcolumn not in columns:
            columns.append(self._hashcolumn)

        for _,column in enumerate(columns):
            if not self._check_exists_column(tablename, column):
                sentence = f"ALTER TABLE {tablename} ADD COLUMN {column.lower()} TEXT"
                self._execute(sentence)
                
    def insert_data(self, tablename, data, columns=None):
        columns = self._get_columns(tablename)
        hash_column = columns.pop(0)
        columns.append(hash_column)
        columns_insert=''
        parameters = ''

        for index, c in enumerate(columns):
            columns_insert+=f'"{c.lower()}"'
            if index != len(columns)-1:
                columns_insert+=','
        
        for index, _ in enumerate(data):
            parameters+="?"
            if index != len(data)-1:
                parameters+=","

        sentence=f"""    
                    INSERT INTO {tablename} ({columns_insert})
                    VALUES ({parameters})"""
        self._execute(sentence, data)