import csv
from model.filecontent import FileContent
from config.settings import SqlMapSetting, Settings, ImportSetting
from utils.utils import Hashing
from utils.utils import Util
from utils.ansiprint import AnsiPrint
from lib.file_reader  import FileReader
import os
import sys

class FileManager:
    def __init__(self) -> None:
        self._sqlmap = SqlMapSetting()
        self._delimiter = self._sqlmap.csv_delimiter
        self._char_replacement = {
            "null":None,
            "<blank>":""
        }


    def get_structure(self, filename:str) -> FileContent:
        
        content = FileContent()
        reader = FileReader()
        content.filename = Util.get_filename(filename)
        if os.path.exists(filename):
            
            with open(filename, newline='') as fb:
                
                csv.field_size_limit(sys.maxsize)
                csv_content = csv.DictReader(fb, delimiter=self._delimiter, quotechar='"')
                content.headers = [column.lower() for column in csv_content.fieldnames]
                content.headers.append(Settings.checksum_column)
                
                for line in csv_content:
                    row = []
                    file_base64 = Util.create_filename(line.values(), content.filename)
                    
                    for value in line.values():
                        try:
                            if value is None:
                                row.append(None)
                                continue
                            elif value.lower() in self._char_replacement:
                                value = self._char_replacement[value.lower()]
                        
                            file = reader.get_from_base64(value)

                            if file.content is not None:
                                value = file.content 
                                #file.filename = self._save_file(file.content, file.extension)
                                file.filename = reader.save_file(file.bytearray, file.extension, file_base64)
                                row.append(value)
                            else:
                                decoded_value = None
                                if value is not None:
                                    decoded_value = Util.decode(value)
                                    decoded_value = Util.remove_invalidchars(decoded_value, ImportSetting().valid_chars)
                                row.append(decoded_value)
                            
                        except Exception as e:
                            AnsiPrint.print_debug(e)
                            raise e
                            

                    ## Calculate checksum
                    hash_value = Hashing.get_md5(''.join(value for value in row if value is not None))
                    row.append(hash_value)
                    content.rows.append(row)
        
        return content