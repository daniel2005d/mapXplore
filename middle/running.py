from dbConnector import DbConnector
from config.settings import Settings
from model.result import Result
from enum import Enum
from utils.ansiprint import AnsiPrint
from utils.utils import Util
from utils.colors import Color
from utils.savemanager import SaveManager
from utils.crypto.hashes import Hashes
from datetime import datetime

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
        results_list = []
        queries = self._cursor.create_query_to_all_values(value_to_find, Settings.setting["Query"]["logical_operator"])
        found = False
        for qry in queries:
            table_name = qry["tablename"]

            results = self.run_query(qry["sentence"], value_to_find)
            if results.length > 0:
                results.table_name = table_name
                results_list.append(results)
                found = True
                self._results.append(results)
                AnsiPrint.print(f"Table Name: [bold][chartreuse_1]{table_name}[reset]")
                AnsiPrint.printResult(results)
        if found == False:
            AnsiPrint.print_info(f"Not results found for [yellow]{value_to_find}[reset]")
        
        return results_list
    
    def _get_hashes(self, hash_type:str, text):
        return Hashes.get_hash_value(text.strip(), hash_type)
    
    def _save(self, format:str=None)->str:
        file_format = self._output_settings["format"] if format is None else format
        if file_format in Settings.valid_format_files:
            csv_delimiter = self._output_settings["csvdelimiter"]
            current_date = datetime.now()
            format_date = current_date.strftime("%Y%m%d%H%M%S")
            for item in self._results:
                content = self._export_manager.convert_content_to_plain(item, file_format, csv_delimiter)
                file_name = f"{item.table_name if item.table_name is not None else ''}_{format_date}.{file_format}"
                saved = self._export_manager.save(content, format, file_name)
                AnsiPrint.print_success(f"Saved to [bold]{saved}[reset]")

    def export(self, format:str=None):
        if len(self._results) > 0:
            self._save(format)
        else:
            AnsiPrint.print_info("No queries have been generated yet")

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
                formatted_columns = []
                for key in row:
                    column_value = str(row[key])
                    data,format = Util.is_base64(column_value)
                    column_text, formatted = Color.highlight_text(column_value, value_to_hight_light)
                    columns.append(column_value)
                    if data is not None:
                        if len(column_text) > 500:
                            truncated_text = Color.format(f"{column_text[0:500]}[cyan][{format if format is not None else 'Truncated...'}][reset]")
                            formatted_columns.append(truncated_text)

                    if data is not None and format is not None:
                        if self._output_settings["savefiles"]:
                            AnsiPrint.print_info(f"Saving file of the [yellow]{key}[end] column")
                            self._export_manager.save(data, format)
                    else:
                        formatted_columns.append(column_text)

                information.formatted_rows.append(formatted_columns)
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
            results = self._filter_by_value(value)
        
        if results is not None and option != QueryType.VALUES:
            self._results.append(results)
            AnsiPrint.printResult(results)
        
        return results
    


