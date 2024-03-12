import os
from config.settings import Settings
from config.settings import ResultSetting, DatabaseSetting
from dbConnector import DbConnector
import i18n.locale as locale
from lib.save_manager import SaveManager
from lib.crypto.hashes import Hashes
from model.result import Result, QueryResult, QueryType
from utils.ansiprint import AnsiPrint
from utils.colors import Color


class DataManager:
    def __init__(self) -> None:
        self._results = []
        self._export_manager = SaveManager()
        self._cursor = None
        
    def _validate_arguments(self) -> bool:
        result = True
        if DatabaseSetting().database_name is None:
            result = False
            AnsiPrint.print_error(locale.get("databasenull"))
        
        return result

    def _create_dbCursor(self):
        if self._validate_arguments():
            db = DbConnector(database=DatabaseSetting().database_name, host=DatabaseSetting().host, 
                            username=DatabaseSetting().username, password=DatabaseSetting().password, 
                            dbms=DatabaseSetting().dbms)
            self._cursor = db._createDBEngine()
            
    
    def _get_values_to_find(self, word:str)->str:
        criterial = []
        words = word.split(',')
        for value in words:
            criterial.append(value)
            
        return criterial
    
    def _save_results(self, value:str, criterial:QueryType, results:list[Result]) -> bool:
        if results.length > 0:
            values = [info for info in self._results if info.criterial == criterial and info.value == value]
            if len(values) == 0:
                self._results.append(QueryResult(criterial=criterial, results=results, value = value))
            else:
                values[0].append(results)

            return True
        else:
            return False
    
    def _filter_tables(self, table_name) -> list[Result]:
        return self._cursor.search_tables(table_name if table_name != '*' else None )
    
    def _filter_columns(self, column_name)-> list[Result]:
        return self._cursor.search_columns(column_name)

    def _filter_by_value(self, value_to_find)-> None:
        queries=[]
        values = []
        
        for value in self._get_values_to_find(value_to_find):
            values.append(value)
            queries += self._cursor.create_query_to_all_values(value)
        
        found = False
        total = 0
        for qry in queries:
            #AnsiPrint.print(' '*(len(qry.tablename)*10))
            results = self.run_query(qry.sentence, qry.word)
            
            if results.length > 0:
                total+=results.length
                results.table_name = qry.tablename
                found = True
                #self._results.append(results)
                self._save_results(qry.tablename, QueryType.VALUES, results)
                AnsiPrint.print(f"Table Name: [bold][chartreuse_1]{qry.tablename}[reset]")
                AnsiPrint.printResult(results)

        if found == False:
            AnsiPrint.print_info(locale.get("notfound").format(word='\r\n'.join(values)))
        else:
            AnsiPrint.print(locale.get("summary"))
            AnsiPrint.print(locale.get("summary_total").format(length=total))
        
        return None
    
    def _get_hashes(self, hash_type:str, text):
        return Hashes.get_hash_value(text.strip(), hash_type)
    
    def _save(self, format:str=None)->None:
        """Save results to setting format
        Args:
            format (str, optional): HTML or CSV. Defaults to None.
        """
        file_format = ResultSetting().format if format is None else format
        if file_format in Settings.valid_format_files:
            file = self._export_manager.convert_content_to_plain(self._results)
            AnsiPrint.print_locale("saved_results", saved=file)
            
    def clean(self):
        length_results = len(self._results)
        self._results.clear()
        AnsiPrint.print_locale("clean_results", num=length_results)

    def export(self, format:str=None):
        if len(self._results) > 0:
            self._save(format)
        else:
            AnsiPrint.print_info(locale.get("cannot_export"))
    
    def table_count_rows(self):
        self._create_dbCursor()
        tables = self._cursor.get_tables_count()
        AnsiPrint.printResult(tables)

    def run_query(self, sentence, value_to_hight_light):
        """Run the query and highlight the text that matches.
    
        Args:
            sentence (str): Run T-SQL query with relevant information
            value_to_hight_light (str): Text to hight light
        """
        result = self._cursor.execute_query(sentence)
        information = Result()
        if result is not None and len(result)>0:
            
            for col in result[0].keys():
                information.headers.append(col)

            for row in result:
                columns = []
                formatted_columns = []
                for key in row:
                    column_value = str(row[key])
                    column_formatted,_ = Color.highlight_text(column_value, value_to_hight_light) #self._format_b64_data(column_value, value_to_hight_light, key)
                    formatted_columns.append(column_formatted)
                    columns.append(column_value)

                information.formatted_rows.append(formatted_columns)
                information.rows.append(columns)

        return information

    def run(self, option:QueryType, value, hash_type:str=None) -> Result:
        try:
            results = None
            self._create_dbCursor()
            if self._cursor is not None:
                if hash_type is not None:
                    hashes = []
                    for text in value.split(','):
                        hashes.append(self._get_hashes(hash_type, text))
                    value=','.join(hashes)

                if option == QueryType.TABLES:
                    results = self._filter_tables(value) #self._cursor.search_tables(value)
                elif option == QueryType.COLUMNS:
                    results = self._filter_columns(value)
                elif option == QueryType.VALUES:
                    results = self._filter_by_value(value)
                
                if results is not None and option != QueryType.VALUES:
                    criterial = "Tables" if option == QueryType.TABLES else "Columns"

                    if self._save_results(criterial, option, results):
                        AnsiPrint.printResult(results)
                        AnsiPrint.print(locale.get("summary"))
                        AnsiPrint.print(locale.get("summary_total").format(length=results.length))
                    else:
                        AnsiPrint.print(locale.get("notfound").format(word=value))
                        

        except Exception as e:
            AnsiPrint.print_error(e)

        return results
    
    def select(self, tables:list[str]) -> None:
        self._create_dbCursor()
        for tbl in tables.split(','):
            if self._cursor.check_exists_table(tbl):
                table = self._cursor.select_table(tbl)
                AnsiPrint.printResult(table)
            else:
                AnsiPrint.print_locale("table_not_exists",table_name=tbl)
