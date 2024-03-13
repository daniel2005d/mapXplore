from dbConnector import DbConnector
from config.settings import SqlMapSetting, DatabaseSetting
from config.settings import Settings
from utils.ansiprint import AnsiPrint
from lib.stopwatch import Stopwatch
from lib.file_manager import FileManager
from model.result import Result
import i18n.locale as locale
import os


class DataImporter():
    def __init__(self) -> None:
        self._summary = None
        self._db = None

    def _bind_config(self):
        self._database = None
        if SqlMapSetting().database:
            self._database = SqlMapSetting().database
        self._directory = SqlMapSetting().file_input
        self._delimiter = SqlMapSetting().csv_delimiter
        self._dbConfig = DatabaseSetting()
        
    
    def _get_connection(self, database:str=None):

        connection = DbConnector(database=database if database is not None else self._database, host=self._dbConfig.host, 
                    username=self._dbConfig.username, password=self._dbConfig.password, 
                    dbms=self._dbConfig.dbms)
        
        self._db = connection._createDBEngine()
        return self._db
        
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

    def create_tables(self, database:str):

        files = SqlMapSetting().get_files_ofDatabase()
        for file in files:
            try:
                self._summary["files"].append(file["filename"])
                file_path = file["path"]
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
        ### Get Dat file structure and information
        AnsiPrint.print_locale("import.reading_file", end=' '*10, filename=file_name)
        file_content = csv.get_structure(path)
        ## Create Table and Columns
        table_columns = file_content.headers
        if file_name not in self._summary["tables"]:
            self._summary["tables"].append(file_name)
        """Create tables
        """
        AnsiPrint.print(f"\rBinding [cyan]{file_name}[reset] [{len(file_content.rows)}/{len(file_content.rows)}]", end=' '*10)
        db.create_table(file_name, table_columns)
        db.insert_many(file_name,file_content.rows, table_columns)
        self._summary["rows"]+=len(file_content.rows)
        AnsiPrint.print(f"\rBinding [cyan]{file_name}[green] [Success][reset]", end=' '*10)

    def start(self):
        old_db = DatabaseSetting().database_name
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
            databases = SqlMapSetting().get_databases()
            if databases is not None:
                for name in databases:
                    SqlMapSetting().database=name
                    self._summary["databases"].append(name.lower())
                    AnsiPrint.print(f"\r\nCreating database [yellow][bold]{name.lower()}[reset]")

                    db = self._get_connection(Settings.get_principal_db(self._dbConfig.dbms))
                    db.create_database(name)
                    self.create_tables(name)
            
            stopwatch.stop()
            self._summary["elapsed"]= str(stopwatch)
            self._print_summary()
        except Exception as e:
            AnsiPrint.print_error(e)
        finally:
            SqlMapSetting().database = old_db
