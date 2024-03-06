from config.settings import Settings
from config.settings import ResultSetting
import os
from model.result import Result
from jinja2 import Environment, FileSystemLoader
from utils.utils import Hashing

class SaveManager:
    def __init__(self) -> None:
        self._results = ResultSetting() #Settings.setting["Results"]
        self._output = self._results.output
        self._format = self._results.format
        self._delimiter = self._results.csv_delimiter
        if self._output is None:
            home = os.path.expanduser("~")
            self._output = os.path.join(home,'.local','share','mapXplore')
            self._results.output = self._output

    def _create_directory(self, directory:str):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _write_content(self, content, name):
        
        if isinstance(content, bytes):
            with(open(name,'wb')) as fb:
                fb.write(content)
        else:
            with(open(name,'w')) as fb:
                fb.write(content)

    def save(self, content, format, name=None, directory:str=None) -> str:
        output_directory = directory if directory is not None else self._output
        self._create_directory(output_directory)
        if name is None:
            
            #current_date = datetime.now()
            #format_date = current_date.strftime("%Y%m%d%H%M%S")
            name = Hashing.get_md5(content)
            if format is not None:
                name+=f".{format}"
        
        path = os.path.join(output_directory, name)

        self._write_content(content, path)
        return path
    
    def convert_content_to_plain(self, items:Result, format:str, delimiter:str=None)->str:
        if format == 'csv':
            return self.convert_to_csv(items, delimiter)
        if format == 'html':
            return self.convert_to_html(items)

    def convert_to_html(self, items:Result):
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template('/templates/result.html')
        output = template.render(headers=items.headers, 
                                rows=items.rows, 
                                formatted_rows=items.formatted_rows,
                                table_name=items.table_name)
        return output

    def convert_to_csv(self, items:Result, delimiter:str):
        text=delimiter.join(items.headers)
        text+='\r\n'
        for row in items.rows:
            text+=delimiter.join(row)
            text+="\r\n"
        return text
    