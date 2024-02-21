import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from db import DataBase
from utils import CastDB

class PostgreSQL(DataBase):

    def _get_cursor(self):
            self._conn = psycopg2.connect(dbname=self._database, user=self.username, password=self.password, host=self.host)
            self._conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
            cursor = self._conn.cursor()
            return cursor
                
    def _destroy(self, cursor):
        cursor.close()
        self._conn.close()

    def _execute(self, sentence, values=None):
        try:
            cur = self._get_cursor()
            generated = cur.execute(sentence, values)
            self._conn.commit()
            self._destroy(cur)
            return generated
        except Exception as e:
            raise e
    
    def _select(self, sentence: str, values=None, showColumns = False):
        rows = []
        cur = self._get_cursor()
        cur.execute(sentence, values)
        results = cur.fetchall()
        if showColumns:
            column_names = [desc[0] for desc in cur.description]
            for row in results:
                row_with_column_names = {}
                for idx, value in enumerate(row):
                    row_with_column_names[column_names[idx]] = value
                rows.append(row_with_column_names)
        else:
            for row in results:
                rows.append(row)

        if len(rows)>0:
          return rows
        
        return None

    def _check_exists_db(self, name:str) -> bool:
        sentence = """
                        SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower(%s);
                    """
        db = self._select(sentence, (name,))
        return db is not None

    def _check_exists_column(self, tablename:str, columnname:str) ->bool:
        sentence = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s  and column_name=%s"
        column = self._select(sentence, (tablename, columnname))
        return column is not None

    def _get_columns(self, tablename:str):
        sentence = f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s"
        columns = self._select(sentence, (tablename,))
        return columns

    def _get_columns_from_table(self, tablename:str):
        columns = []
        for t in self._tables:
            if t["table"] == tablename:
                columns = t["columns"]
        
        if len(columns) == 0:
            rows = self._get_columns(tablename)
            if rows:
                columns = [item[0] for item in rows]
                self._tables.append({"table":tablename, "columns":columns})
        
        return columns
    def execute_query(self, query:str):
        return self._select(query, showColumns=True)
    
    def create_query_to_all_values(self, value_to_find, operator='or'):
        rows = self.get_tables_and_columns()
        queries = []
        for row in rows:
            tablename = row[0]
            columns = row[1]#.strip('{}').split(',')
            sentence = f"Select * from {tablename} where "
            for index, col in enumerate(columns):
                definition = col.split(':')
                column_name = f'"{definition[0]}"'
                data_type = definition[1]
                if index == 0:
                    sentence+=f"{CastDB.cast_column(column_name, data_type)} ilike '%{value_to_find}%' "
                else:
                    sentence+=f"{operator} {CastDB.cast_column(column_name, data_type)} ilike '%{value_to_find}%' "
            
            queries.append({"tablename":tablename,"sentence":sentence})
        
        return queries
        
    
    def get_tables_and_columns(self):
        sentence = """
                    Select table_name, array_agg(column_name||':'||data_type) as columns
                    from information_schema.columns where table_schema='public' group by table_name
        """
        rows = self._select(sentence)
        return rows
    
    def _value_exists(self, tablename:str, hash:str)->bool:
        sentence = f"""
                    Select * from {tablename} where {self._hashcolumn}=%s
                    """
        return not self._select(sentence, (hash,)) is None

    """
    Check if Table exists
    """
    def check_exists_table(self, tablename:str) -> bool:
        sentence = """
                        select * from pg_tables where schemaname='public' and tablename=%s
                    """
        db = self._select(sentence, (tablename,))
        return db is not None

    """
    If database exists, drop and create
    """
    def create_database(self, dbname:str):
        if self._recreate:
          self._execute(f'DROP DATABASE IF EXISTS {dbname.lower()}')

        dbexists = self._check_exists_db(dbname)
        if not dbexists:
          create_db = f'CREATE DATABASE "{dbname.lower()}" WITH OWNER={self.username} TEMPLATE template0'
          self._execute(create_db)
        
   
    def create_table(self, name:str, columns=None):
        try:
           dbexists = self._check_exists_db(self._database)
           if dbexists:
               sentence = f"""
                           CREATE TABLE IF NOT EXISTS public.{name}()
                           """
               self._execute(sentence)
               if self.check_exists_table(name):
                 self.create_columns(name, columns)
        except Exception as e:
            raise e

    


    def create_columns(self, tablename:str, columns):
        try:
            if not self._hashcolumn in columns:
                columns.append(self._hashcolumn)

            sentence = f"ALTER TABLE {tablename}\n"

            for index,column in enumerate(columns):
                if not self._check_exists_column(tablename, column):
                    column_type = "TEXT"
                    if column.lower() == self._hashcolumn:
                        column_type = "varchar(50)"

                    sentence += f"ADD COLUMN \"{column.lower()}\" {column_type}"
                    sentence+=","
            
            if sentence.endswith(","):
                sentence=sentence[:-1]
            if "COLUMN" in sentence:
              self._execute(sentence)
              if self._hashcolumn in sentence:
                  self._execute(f"CREATE UNIQUE INDEX IF NOT EXISTS {tablename}_{self._hashcolumn}_idx ON public.{tablename} USING btree ({self._hashcolumn})")
        except Exception as e:
            raise e
  
    def insert_data(self, tablename, data, columns=None):
        try:
            if columns is None:
                columns = self._get_columns_from_table(tablename)
            elif not self._hashcolumn in columns:
                columns.append(self._hashcolumn)


            parameters = ''
            columns_insert=''
            
            """
            Calculate MD5 for all data
            """
            for index, c in enumerate(columns):
                columns_insert+=f'"{c.lower()}"'
                if index != len(columns)-1:
                    columns_insert+=','

            for index, column in enumerate(data):
                parameters+="%s"
                if index != len(data)-1:
                    parameters+=","
            
            

            sentence=f"""    
                        INSERT INTO {tablename} ({columns_insert})
                        VALUES ({parameters})
                        ON CONFLICT ({self._hashcolumn}) DO NOTHING
                    """
            self._execute(sentence, data)
        except Exception as e:
            raise e
    
    def search_tables(self, filter:str):
        tables = self._select(f"Select table_name from information_schema.tables where table_name ilike '%{filter}%' and table_type='BASE TABLE'")
        return tables
    
    def search_columns(self, filter:str):
        columns = self._select(f"Select table_name,column_name from information_schema.columns where column_name ilike '%{filter}%' and table_schema!='pg_catalog'")
        return columns
    
    #def search_values(self, )