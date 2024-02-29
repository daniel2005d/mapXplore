from dbConnector import DbConnector
from config.settings import Settings
from utils.ansiprint import AnsiPrint
from utils.stopwatch import Stopwatch
from middle.filemanager import FileManager
from middle.mapexception import MapXploreException
from model.filecontent import FileContent
from model.result import Result
import i18n.locale as locale
import os


class Import():
    def __init__(self) -> None:
        self._summary = None
        self._db = None

    
    def _bind_config(self):
        config = Settings.setting["sqlmap"]
        self._database = None
        if config["database"] is not None and config["database"] != "":
            self._database = config["database"]
        self._directory = config["input"]
        self._delimiter = config["csvdelimiter"]
        self._dbConfig = Settings.setting["Database"]
        
    
    def _get_connection(self, database:str=None):

        connection = DbConnector(database=database if database is not None else self._database, host=self._dbConfig["host"], 
                    username=self._dbConfig["username"], password=self._dbConfig["password"], 
                    dbms=self._dbConfig["dbms"])
        
        self._db = connection._createDBEngine()
        return self._db
        

    def _get_directories(self, directory:str):
        dump_dir = os.path.join(directory,'dump')
        if os.path.exists(dump_dir):
            directories = [name for name in os.listdir(dump_dir) if os.path.isdir(os.path.join(dump_dir, name))]
            return directories,dump_dir
        else:
            AnsiPrint.print_error(locale.get('dir_not_not').format(directory=dump_dir))
            return [],None
    
    def _print_summary(self):
        summary = Result()
        if self._summary is not None:
            AnsiPrint.print_info(locale.get("import.databasetitle"))
            headers = locale.get("import.summary_table_titles")
            summary.headers=headers
            for db in self._summary["databases"]:
                summary.rows.append(['Database', db])
            
            for table in self._summary["tables"]:
                summary.rows.append(['Table', table])
            
            for file in self._summary["files"]:
                summary.rows.append(['File', file])

            summary.rows.append([locale.get("import.totaltitle"), self._summary["rows"]])
            summary.rows.append([locale.get("import.total_time_title"), self._summary["elapsed"]])

            AnsiPrint.printResult(summary)
    
    def start(self):
        try:
            stopwatch = Stopwatch()
            stopwatch.start()
            self._summary = {
                "databases":[],
                "tables":[],
                "rows":0,
                "files":[],
                "elapsed":""

            }
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

                    self._summary["databases"].append(dir.lower())
                    AnsiPrint.print(f"Creating database [yellow][bold]{dir.lower()}[reset]")

                    db = self._get_connection(Settings.principal_databases.get(self._dbConfig["dbms"]))
                    db.create_database(dir)
                    self.create_tables(dir, os.path.join(dump_dir, dir))
            else:
                AnsiPrint.print_error(f'The {dump_dir} directory does not exists.')
            
            stopwatch.stop()
            self._summary["elapsed"]= str(stopwatch)
            self._print_summary()
        except Exception as e:
            AnsiPrint.print_error(e)

    def create_tables(self, database:str, directory:str):
        
        files = []
        for name in os.listdir(directory):
            if not name.startswith("."):
                if os.path.isfile(os.path.join(directory, name)):
                    files.append(name)

        for file in files:
            try:
                self._summary["files"].append(file)
                file_path = os.path.join(directory, file)
                self.insert_data(database,file_path)
            except Exception as e:
                txt = f"Error into {file} => {str(e)}"
                AnsiPrint.print_error(txt)

    def insert_data(self, database:str, path:str):
        csv = FileManager()
        db = self._get_connection(database)
        file = os.path.basename(path)
        index_ext = file.index('.')
        file_name = file[:index_ext].lower()
        file_content = csv.get_structure(path)
        ## Create Table and Columns
        table_columns = file_content.headers
        if file_name not in self._summary["tables"]:
            self._summary["tables"].append(file_name)
        db.create_table(file_name, table_columns)
        db.insert_many(file_name,file_content.rows, table_columns)
        AnsiPrint.print(f"\rBinding [cyan]{file_name}[reset] [{len(file_content.rows)}/{len(file_content.rows)-1}]", end='')
        self._summary["rows"]+=len(file_content.rows)
        # for index, line in enumerate(file_content.rows):
        #     try:
        #         self._summary["rows"]+=index
        #         AnsiPrint.print(f"\rBinding [cyan]{file_name}[reset] [{index}/{len(file_content.rows)-1}]", end='')
        #         db.insert_data(file_name, line, table_columns)
        #     except Exception as e:
        #         txt = f"Error into {file_name} index {index} {e}"
        #         AnsiPrint.print_error(txt)
        
        AnsiPrint.print(f"\rBinding [cyan]{file_name}[green] [Success][reset]")
