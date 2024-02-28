import csv
from model.filecontent import FileContent
from config.settings import Settings
from utils.utils import Hashing
import os


class FileManager:
    def __init__(self) -> None:
        self._sqlmap = Settings.setting["sqlmap"]
        self._delimiter = self._sqlmap["csvdelimiter"]

    def _get_filename(self, filename:str)->str:
        full_name = os.path.basename(filename)
        name = os.path.splitext(full_name)[0]
        return name
    
    def _decode(self, text:str)->str:
        decoded = text
        try:
            if not text.isdigit():
                decoded = text.encode('latin').decode('unicode_escape')
        except:
            pass
        
        return decoded

    def get_structure(self, filename:str) -> FileContent:
        content = FileContent()
        content.filename = self._get_filename(filename)
        if os.path.exists(filename):
            with open(filename, newline='') as fb:
                csv_content = csv.DictReader(fb, delimiter=self._delimiter, quotechar='"')
                content.headers = [column.lower() for column in csv_content.fieldnames]
                content.headers.append(Settings.checksum_column)
                for line in csv_content:
                    row = []
                    for value in line.values():
                        row.append(self._decode(value))
                    
                    ## Calculate checksum
                    hash_value = Hashing.get_md5(''.join(row))
                    row.append(hash_value)
                    content.rows.append(row)
        return content