import csv
from model.filecontent import FileContent
from config.settings import SqlMapSetting, Settings
from utils.utils import Hashing
from utils.utils import Util
from utils.file_reader  import FileReader
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
                    for value in line.values():
                        if value.lower() in self._char_replacement:
                            value = self._char_replacement[value.lower()]
                        
                        file = reader.get_from_base64(value)
                        if file.content is not None:
                            value = f"[cyan]{file.content})({file.extension})[{file.filename}][reset]"
                            row.append(value)
                        else:
                            row.append(Util.decode(value))

                    ## Calculate checksum
                    hash_value = Hashing.get_md5(''.join(value for value in row if value is not None))
                    row.append(hash_value)
                    content.rows.append(row)
        
        return content