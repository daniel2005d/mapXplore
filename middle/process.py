from dbConnector import DbConnector
from utils.ansiprint import AnsiPrint
from config.settings import Settings
from utils.utils import Hashing
import re
import os

class Import():
    def __init__(self, args) -> None:
        Settings.sqlmap_config(args)

    
    def _bind_config(self):
        config = Settings.setting["sqlmap"]
        self._database = config["database"]
        self._directory = config["input"]
        self._recreate = config["recreate"]
        self._delimiter = config["csvdelimiter"]
        self._dbConfig = Settings.setting["Database"]
    
    def _get_connection(self, database:str):
        connection = DbConnector(database= database if database is not None else self._database, host=self._dbConfig["host"], 
                    username=self._dbConfig["username"], password=self._dbConfig["password"], 
                    dbms=self._dbConfig["dbms"])
        
        db = connection._createDBEngine()
        return db
        

    def _get_directories(self, directory:str):
        dump_dir = os.path.join(directory,'dump')
        if os.path.exists(dump_dir):
            directories = [name for name in os.listdir(dump_dir) if os.path.isdir(os.path.join(dump_dir, name))]
            return directories,dump_dir
        
    def _split_string(self, string):
        pattern = f'[^{self._delimiter}\"]+|\"(?:[^\"]*)\"'
        matches = re.findall(pattern, string)
        try:
        
            for index, match in enumerate(matches):
                match = match.encode('latin').decode('unicode_escape')
                match = re.sub('^\"|\"$', '', match)
                matches[index] = match
        except:
            pass
                
        return matches
    

    def start(self):
        self._bind_config()
        directories = []
        
        dump_dir = ""
        if self._database is None:
            directories,dump_dir = self._get_directories(self._directory)
        else:
            dump_dir = os.path.join(self._directory,"dump")
            if not os.path.exists(dump_dir):
                AnsiPrint.print_error(f"Directory {dump_dir} does not exists")

            directories.append(self._database)

        if directories is not None:
            for dir in directories:
                AnsiPrint.print(f"Creating database [yellow][bold]{dir.lower()}[reset]")

                db = self._get_connection(db.principal_database)
                db.create_database(dir)
                self.create_tables(dir, os.path.join(dump_dir, dir))
        else:
            AnsiPrint.print_error(f'The {dump_dir} directory does not exists.')

    def create_tables(self, database:str, directory:str):
        
        files = []
        for name in os.listdir(directory):
            if not name.startswith("."):
                if os.path.isfile(os.path.join(directory, name)):
                    files.append(name)

        for file in files:
            try:
                file_path = os.path.join(directory, file)
                self.insert_data(database,file_path)
            except Exception as e:
                txt = f"Error into {file} => {str(e)}"
                AnsiPrint.print_error(txt)

    def insert_data(self, database:str, path:str):
        db = self._get_connection(database)
        file = os.path.basename(path)
        index_ext = file.index('.')
        file_name = file[:index_ext].lower()
        AnsiPrint.print(f"Dumping [green]{file}[reset]")
        csv = open(path, 'r')
        message = ""
        lines = csv.readlines()
        columns = []
        for index, line in enumerate(lines):
            try:
                
                line = line.strip()
                if line != "":
                    if index > 0:
                        line+=f"{self._delimiter}{Hashing.get_md5(line)}"
                    
                    if file_name.startswith("reports"):
                        print("")
                    fields = self._split_string(line.strip())
                    
                    if index == 0:
                        columns = [string.lower() for string in fields]
                        table_columns = db._get_columns_from_table(file_name)
                        difference = set(columns)-set(table_columns)
                        if not db.check_exists_table(file_name):
                            message = f"Creating Table [cyan]{file_name}[reset]"
                            AnsiPrint.print(message)
                            db.create_table(file_name, fields)
                        elif len(difference) > 0:
                            db.create_columns(file_name, list(difference))
                    else:
                        finished = ""
                        
                        if index>=len(lines)-1:
                            finished = " Ok!"

                        print(f"\rBinding [{file_name}] [{index}/{len(lines)}]", end=finished)
                        db.insert_data(file_name, fields, columns)
            except Exception as e:
                txt = f"Error into {file_name} index {index} {e}"
                AnsiPrint.print_error(txt)
        
