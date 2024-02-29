import csv
from model.filecontent import FileContent
from config.settings import Settings
from utils.utils import Hashing
from utils.utils import Util
import os


class FileManager:
    def __init__(self) -> None:
        self._sqlmap = Settings.setting["sqlmap"]
        self._delimiter = self._sqlmap["csvdelimiter"]


    def get_structure(self, filename:str) -> FileContent:
        content = FileContent()
        content.filename = Util.get_filename(filename)
        if os.path.exists(filename):
            with open(filename, newline='') as fb:
                csv_content = csv.DictReader(fb, delimiter=self._delimiter, quotechar='"')
                content.headers = [column.lower() for column in csv_content.fieldnames]
                content.headers.append(Settings.checksum_column)
                for line in csv_content:
                    row = []
                    for value in line.values():
                        row.append(Util.decode(value))
                    
                    ## Calculate checksum
                    hash_value = Hashing.get_md5(''.join(row))
                    row.append(hash_value)
                    content.rows.append(row)
        return content