import os
import sqlite3
from typing import List
from db import DataBase
from config.settings import ResultSetting, DatabaseSetting
from lib.save_manager import SaveManager
from model.query import Query
from model.result import Result



class SQLite(DataBase):
    
    @property
    def principal_database(self)->str:
        return ""

    def _get_db_file(self):
        manager = SaveManager()
        path = os.path.join(ResultSetting().output,DatabaseSetting().database_name, "db")
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
        rows=[]
        if values is not None:
            cursor.execute(sentence, values)
        else:
            cursor.execute(sentence)
        results = cursor.fetchall()

        if showColumns:
            column_names = [desc[0] for desc in cursor.description]
            for row in results:
                row_with_column_names = {}
                for idx, value in enumerate(row):
                    row_with_column_names[column_names[idx]] = value
                rows.append(row_with_column_names)
        else:
            for row in results:
                rows.append(row)
        
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

    def _check_exists(self, table_name, column_name, value)->bool:
            result = self._select(f"Select * from {table_name} where {column_name}=? LIMIT 1", (value,))
            return len(result)>0
    
    def execute_query(self, query:str):
        return self._select(query, showColumns=True)

    def create_database(self, dbname:str):
        dbname = dbname.lower()
        path_db = self._get_db_file()
        db_file = os.path.join(path_db, dbname+".db")
        if os.path.exists(db_file):
            os.remove(db_file)
        self._get_cursor(dbname)
        self._conn.close()
    
    
    def check_exists_table(self, tablename:str) -> bool:
        table = self._select("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tablename,))
        return len(table)>0
    
    def get_tables_count(self) -> Result:
        result = Result(headers=['Table', "Rows"])
        tables = self.get_tables()
        for tbl in tables:
            table_name = tbl[0]
            rows = self._select(f"Select count(*) from {table_name}")
            for row in rows:
                result.rows.append([table_name, row[0]])
        
        return result

    def get_tables(self):
        tables = self._select("Select name from sqlite_master where type='table'")
        return tables
    
    def search_tables(self, filter:str=None):
        result = Result(headers=['tables'])
        if filter:
            tables = self._select(f"SELECT name FROM sqlite_master WHERE type='table' AND name like '%{filter}%'")
        else:
            tables = self.get_tables()
        if tables:
            for table in tables:
                result.rows.append(table)
        
        return result

    def search_columns(self, filter:str) -> Result:
        result = Result(headers=['table_name','column_name'])
        tables = self.get_tables()
        for tbl in tables:
            table_name = tbl[0]
            columns = self._get_columns(table_name)
            column_names = [info for info in columns if filter in info]
            for col in column_names:
                result.rows.append([table_name,col])
        return result

    def get_tables_and_columns(self):
        tables = self.get_tables()
        results = []
        for tbl in tables:
            columns = self._get_columns(tbl[0])
            results.append({"table_name":tbl[0], "columns":columns})

        return results


    def create_query_to_all_values(self, value_to_find, operator='or'):
        rows = self.get_tables_and_columns()
        queries:List[Query] = []
        for row in rows:
            query=""
            table_name = row["table_name"]
            columns_list = ','.join(f'[{col}]' for col in row["columns"])
            for index, col in enumerate(row["columns"]):
                if index == 0:
                    query = f"[{col}] like '%{value_to_find}%'"
                else:
                    query += f" {operator} [{col}] like '%{value_to_find}%'"
                
            sentence = f"Select {columns_list} from {table_name} where {query}"
            queries.append(Query(word=value_to_find, sentence=sentence, tablename=table_name))
        
        return queries
        

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
                sentence = f"ALTER TABLE {tablename} ADD COLUMN [{column.lower()}] TEXT"
                self._execute(sentence)
                
    def insert_data(self, tablename, data, columns=None):
        exists = self._check_exists(tablename, self._hashcolumn, data[-1])
        if  exists == False:
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

    def _get_insert_sentence(self, tablename, data, columns=None):
        if columns is None:
                columns = self._get_columns_from_table(tablename)
        elif not self._hashcolumn in columns:
            columns.append(self._hashcolumn)
        
        columns_lower = ', '.join(f'"{column.lower()}"' for column in columns)
        parameters = ','.join('?' for _ in columns)

        sentence=f"""    
                    INSERT INTO {tablename} ({columns_lower})
                    VALUES ({parameters})
                """

        return sentence

    def _executemany(self, sentence, values=None):
        try:
            cur = self._get_cursor()
            generated = cur.executemany(sentence, values)
            self._conn.commit()
            return generated
        except Exception as e:
            raise e


    def insert_many(self, tablename, data, columns=None):
        try:
            sentence = self._get_insert_sentence(tablename, data, columns)
            self._executemany(sentence, data)
        except Exception as e:
            raise e
    
    # def select_table(self, table_name:str) -> Result:
    #     result = Result()
    #     rows = self._select(f"Select * from {table_name}", showColumns=True)
    #     if rows:
    #         result.headers=list(rows[0].keys())
    #         for row in rows:
    #             result.rows.append(list(row.values()))
        
    #     return result


