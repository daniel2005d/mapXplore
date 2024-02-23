from dbConnector import DbConnector
from config.settings import Settings
from model.result import Result
from enum import Enum
from utils.ansiprint import AnsiPrint
from utils.utils import Util
from utils.colors import Color
from utils.savemanager import SaveManager
from utils.crypto.hashes import Hashes

class QueryType(Enum):
    NONE = 0
    TABLES = 1
    COLUMNS = 2
    VALUES = 3
    ALL = 4

class Running:
    def __init__(self) -> None:
        self._dbConfig = Settings.setting["Database"]
        self._results = []
        self._export_manager = SaveManager()
        self._output_settings = Settings.setting["Results"]

    def _create_dbCursor(self):
        db = DbConnector(database=self._dbConfig["database"], host=self._dbConfig["host"], 
                         username=self._dbConfig["username"], password=self._dbConfig["password"], 
                         dbtype=self._dbConfig["dbtype"])
        self._cursor = db._createDBEngine()
    
    def _filter_by_value(self, value_to_find):
        queries = self._cursor.create_query_to_all_values(value_to_find, Settings.setting["Query"]["logical_operator"])
        found = False
        for qry in queries:
            table_name = qry["tablename"]
            results = self.run_query(qry["sentence"], value_to_find)
            if results.length > 0:
                found = True
                self._results.append(results)
                AnsiPrint.print(f"Table Name: [bold][chartreuse_1]{table_name}[reset]")
                AnsiPrint.printResult(results)
        if found == False:
            AnsiPrint.print_info(f"Not results found for [yellow]{value_to_find}[reset]")
    
    def _get_hashes(self, hash_type:str, text):
        return Hashes.get_hash_value(text.strip(), hash_type)


    """
    Run the query and highlight the text that matches.
    """
    def run_query(self, sentence, value_to_hight_light):
        result = self._cursor.execute_query(sentence)
        information = Result()
        if result is not None:
            
            for col in result[0].keys():
                information.headers.append(col)

            for row in result:
                columns = []
                for key in row:
                    column_value = str(row[key])
                    data,format = Util.is_base64(column_value)
                    column_text, formatted = Color.highlight_text(column_value, value_to_hight_light)
                    if data is not None:
                        if len(column_text) > 500:
                            truncated_text = Color.format(f"{column_text[0:500]}[cyan][{format if format is not None else 'Truncated...'}][reset]")
                            columns.append(truncated_text)

                    if data is not None and format is not None:
                        if self._output_settings["savefiles"]:
                            AnsiPrint.print_info(f"Saving file of the [yellow]{key}[end] column")
                            self._export_manager.save(data, format)
                    else:
                        columns.append(column_text)

                information.rows.append(columns)

        return information

    
    def run(self, option:QueryType, value, hash_type:str=None) -> Result:
        results = None
        self._create_dbCursor()
        if hash_type is not None:
            value = self._get_hashes(hash_type, value)

        if option == QueryType.TABLES:
            results = self._cursor.search_tables(value)
        elif option == QueryType.COLUMNS:
            results = self._cursor.search_columns(value)
        elif option == QueryType.VALUES:
            self._filter_by_value(value)
        
        if results is not None:
            self._results.append(results)
            AnsiPrint.printResult(results)


