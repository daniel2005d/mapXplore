from config.settings import Settings
from config.settings import ResultSetting
import os
from datetime import datetime
from model.result import Result
from jinja2 import Environment, FileSystemLoader
import base64

class SaveManager:
    def __init__(self) -> None:
        self._results = ResultSetting() #Settings.setting["Results"]
        self._output = self._results.output
        self._savefiles = self._results.save_files
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

    def save(self, content, format, name=None) -> str:
        self._create_directory(self._output)
        if name is None:
            current_date = datetime.now()
            format_date = current_date.strftime("%Y%m%d%H%M%S")
            name = f"{format_date}.{format}"
        
        path = os.path.join(self._output, name)

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
    