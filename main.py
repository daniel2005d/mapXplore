"""
Import the CSV database dump generated by SQLMap 
into personal PostgrsSQL database
"""
import os
import sys
from database.connection import Connection
from database.PostgreSQL import PostgreSQL
from database.MongoDB import MongoDB
from utils import Util, Hashing
import argparse
import re
import threading
import json

class ReadContent():
    def __init__(self,server, username, password, delimiter=',', table=None, recreate=False, database=None,dbtype=None) -> None:
        self._delimiter = delimiter
        self._table= table
        self._recreate = recreate
        self._database = database
        self._connection = Connection(server=server,username=username,password=password)
        self._DEFAULT_DB='postgres'
        self._max_threads = 1
        self._dbtype = dbtype
    
    def _get_directories(self, directory:str):
        dumpdir = os.path.join(directory,'dump')
        if os.path.exists(dumpdir):
          directories = [name for name in os.listdir(dumpdir) if os.path.isdir(os.path.join(dumpdir, name))]
          return directories,dumpdir

    def _createDBEngine(self, database=None, connection=None):
        if self._dbtype == 'postgress':
            return PostgreSQL(self._DEFAULT_DB if database is None else database, self._connection if connection is None else connection)
        elif self._dbtype == 'mongo':
            return MongoDB(self._DEFAULT_DB if database is None else database, self._connection if connection is None else connection)


    def start(self, directory:str):
        directories = []
        dumpdir = ""
        if self._database is None:
          directories,dumpdir = self._get_directories(directory)
        else:
            dumpdir = os.path.join(directory,"dump")
            if not os.path.exists(dumpdir):
                Util.print_error(f"Directory {dumpdir} does not exists")
                sys.exit(-1)

            directories.append(self._database)

        if directories is not None:
            db = self._createDBEngine(self._DEFAULT_DB, self._connection) #DataBase(self._DEFAULT_DB, self._connection)
            db.recreate = self._recreate
            
            for dir in directories:
                Util.print(f"Creating database {dir.lower()}", color="cyan")
                db.create_database(dir)
                self.create_tables(dir, os.path.join(dumpdir, dir))
        else:
            Util.print_error(f'The {dumpdir} directory does not exists.')
            sys.exit(-1)
    
    def _split_string(self, string):
        pattern = f'[^{self._delimiter}\"]+|\"(?:[^\"]*)\"'
        matches = re.findall(pattern, string)
        return matches

    def insert_data(self, database:str, path:str):
        db = self._createDBEngine(database, self._connection)
        db.recreate = self._recreate
        file = os.path.basename(path)
        index_ext = file.index('.')
        file_name = file[:index_ext].lower()
        print("")
        Util.print(f"Dumping {file}", color="blue")

        csv = open(path, 'r')

        message = ""
        lines = csv.readlines()
        columns = []
        for index, line in enumerate(lines):

            try:
                
                line = line.strip()
                if line != "":
                    # if "[" in line:
                    #     line = line.replace("\"","").replace("[","").replace("]","").replace("\\","")
                    if index > 0:
                        # Add md5
                        line+=f"{self._delimiter}{Hashing.get_md5(line)}"
                        
                    fields = self._split_string(line.strip())
                    
                    if index == 0:
                        columns = [string.lower() for string in fields]
                        table_columns = db._get_columns_from_table(file_name)
                        difference = set(columns)-set(table_columns)
                        if not db.check_exists_table(file_name):
                            message = f"Creating Table {file_name}"
                            Util.print(message, color="magenta")
                            db.create_table(file_name, fields)
                        elif len(difference) > 0:
                            db.create_columns(file_name, list(difference))
                    else:
                        finished = ""
                        
                        if index>=len(lines)-1:
                            finished = " Ok!"

                        print(f"\rBinding [{file_name}] [{index}/{len(lines)-1}]", end=finished)
                        db.insert_data(file_name, fields, columns)
            except Exception as e:
                txt = f"Error into {file_name} index {index} {e}"
                Util.print_error(txt)
        
    
    def create_tables(self, database:str, directory:str):
        files = []
        threads = []
        for name in os.listdir(directory):
            
            if self._table is not None:
                if name.startswith(self._table+"."):
                    files.append(name)
            else:
                if not name.startswith("."):
                    if os.path.isfile(os.path.join(directory, name)):
                        files.append(name)

        for file in files:
            try:
                
                file_path = os.path.join(directory, file)
                th = threading.Thread(target=self.insert_data, args=(database,file_path,))
                th.start()
                threads.append(th)
                if len(threads)>= self._max_threads:
                    for index, t in enumerate(threads):
                        t.join()
                        threads.pop(index)
                    
                #self.insert_data(database, file_path)
            except Exception as e:
                txt = f"Error into {file} => {str(e)}"
                Util.print_error(txt)
    
def print_arguments(args):
    print(f"""
            Version: 1.2 \n
            Directory: {args.directory}
            Character: {args.chardelimiter}
            UserName: {args.username}
            Host: {args.host}
            Database: {args.database}
          """)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--directory', help='Sqlmap output directory', required=False)
    parser.add_argument('-c','--chardelimiter',default=',',help='Delimiter of the dump information')
    parser.add_argument('-s','--host', required=False, help='Postgress server IP/Name')
    parser.add_argument('-u', '--username', required=False, help='Username of the database server')
    parser.add_argument('-p', '--password', required=False, help='Username of the database server')
    parser.add_argument('-t', '--table', required=False, help='Specific table to import')
    parser.add_argument('-D', '--database', required=False, help='Specific database to import')
    parser.add_argument('-f', '--force', required=False, help='Recreate all databases', action="store_true")
    parser.add_argument('--dbtype',choices=['postgress','mongo'],default='postgress')
    parser.add_argument('--config', help='Config json file. With parameters options')
    args = parser.parse_args()

    if args.config:
        with open(args.config, 'r') as fb:
            settings = json.load(fb)
            args.directory=settings["directory"]
            args.chardelimiter=settings["chardelimiter"]
            args.username=settings["username"]
            args.host=settings["host"]
            args.password=settings["password"]
            if "database" in settings:
                args.database=settings["database"]
            if "table" in settings:
                args.table=settings["table"]

    print_arguments(args)
    r = ReadContent(delimiter=args.chardelimiter, username=args.username, 
                    server=args.host, password=args.password, table=args.table, 
                    recreate=args.force, database=args.database, dbtype=args.dbtype)
    
    r.start(args.directory)
