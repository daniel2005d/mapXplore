from dbConnector import DbConnector
from config.settings import Settings
from config.settings import ResultSetting, DatabaseSetting
from model.result import Result
from enum import Enum
from utils.ansiprint import AnsiPrint
from utils.utils import Util
from utils.utils import Hashing
from utils.colors import Color
from utils.savemanager import SaveManager
from utils.crypto.hashes import Hashes
from datetime import datetime
import i18n.locale as locale
from base64 import b64encode, b64decode

class QueryType(Enum):
    NONE = 0
    TABLES = 1
    COLUMNS = 2
    VALUES = 3
    ALL = 4

class Running:
    def __init__(self) -> None:
        self._results = []
        self._export_manager = SaveManager()
        self._cursor = None
        self._files = []
    
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

    def _filter_by_value(self, value_to_find):
        results_list = []
        queries=[]
        values = []

        for value in self._get_values_to_find(value_to_find):
            values.append(value)
            queries += self._cursor.create_query_to_all_values(value)
        
        found = False
        total = 0
        for qry in queries:
            AnsiPrint.print(f"[cyan]{qry.tablename}[reset]", end='')
            results = self.run_query(qry.sentence, qry.word)
            AnsiPrint.print(''*(len(qry.tablename)*5),end='\r')
            if results.length > 0:
                total+=results.length
                results.table_name = qry.tablename
                results_list.append(results)
                found = True
                self._results.append(results)
                AnsiPrint.print(f"Table Name: [bold][chartreuse_1]{qry.tablename}[reset]")
                AnsiPrint.printResult(results)

        if found == False:
            AnsiPrint.print_info(locale.get("notfound").format(word='\r\n'.join(values)))
        else:
            AnsiPrint.print(locale.get("summary"))
            AnsiPrint.print(locale.get("summary_total").format(length=total))
        
        return results_list
    
    def _get_hashes(self, hash_type:str, text):
        return Hashes.get_hash_value(text.strip(), hash_type)
    
    def _save(self, format:str=None)->None:
        """Save results to setting format

        Args:
            format (str, optional): HTML or CSV. Defaults to None.
        """
        file_format = ResultSetting().format if format is None else format
        if file_format in Settings.valid_format_files:
            csv_delimiter = ResultSetting().csv_delimiter
            current_date = datetime.now()
            format_date = current_date.strftime("%Y%m%d%H%M%S")
            for item in self._results:
                content = self._export_manager.convert_content_to_plain(item, file_format, csv_delimiter)
                file_name = f"{item.table_name if item.table_name is not None else ''}_{format_date}.{file_format}"
                saved = self._export_manager.save(content, format, file_name)
                AnsiPrint.print_locale("saved_results", saved=saved)
            
            self._save_files()
        

    def _save_files(self) -> None:
        save = SaveManager()
        for item in self._files:
            content = item["content"]
            format = item["format"]
            text = item["text"]
            if format in ['docx','xlsx','ppt','pdf']:
                path = save.save(b64decode(text), format)
            else:
                path = save.save(content, format)

            AnsiPrint.print_locale("savefiles", key=path)
        
        self._files.clear()
    
    
    def _format_b64_data(self, text:str, value_to_hight_light:str, file_name:str):
        """Try to convert text from base64 to plain text
        if savefiles settings its true this file will be save
        Args:
            text (str): Base64 text
            value_to_hight_light (str): Text to hight light
            file_name (str): File name to save

        Returns:
            _type_: _description_
        """
        data,format = Util.is_base64(text)
        if data is not None: # Is Base64 
            
            if format.lower() != 'txt':
                column_formatted = Color.format(f"{data}[cyan][{format if format is not None else 'Truncated... [red][{format}]'}][reset]")
            else:
                text_format = format if format is not None else "fromBase64"
                column_formatted, _ =  Color.highlight_text(data+f"[cyan][{text_format}][reset]", value_to_hight_light)
        else:
            if format is not None:
                column_formatted, _ =  Color.highlight_text(text if format == 'bin' else text[:100]+f"[cyan]{format}[reset]" , value_to_hight_light)
            else:
                column_formatted, _ =  Color.highlight_text(text, value_to_hight_light)
        
        if data is not None and format is not None:
            if {"content":data, "format":format, "text":text} not in self._files:
                self._files.append({"content":data, "format":format, "text":text})
            

        return column_formatted
    
    def export(self, format:str=None):
        if len(self._results) > 0:
            self._save(format)
        else:
            AnsiPrint.print_info(locale.get("cannot_export"))

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
                    column_formatted = self._format_b64_data(column_value, value_to_hight_light, key)
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
                    results = self._cursor.search_tables(value)
                elif option == QueryType.COLUMNS:
                    results = self._cursor.search_columns(value)
                elif option == QueryType.VALUES:
                    results = self._filter_by_value(value)
                
                if results is not None and option != QueryType.VALUES:
                    if results.length>0:
                        self._results.append(results)
                        AnsiPrint.printResult(results)
                        AnsiPrint.print(locale.get("summary"))
                        AnsiPrint.print(locale.get("summary_total").format(length=results.length))
                    else:
                        AnsiPrint.print(locale.get("notfound").format(word=value))
                        

        except Exception as e:
            AnsiPrint.print_error(e)
        return results