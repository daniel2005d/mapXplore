from config.settings import Settings
import os
from datetime import datetime

class SaveManager:
    def __init__(self) -> None:
        self._results = Settings.setting["Results"]
        self._output = self._results["output"]
        self._savefiles = self._results["savefiles"]
        self._format = self._results["format"]
        if self._output == '':
            home = os.path.expanduser("~")
            self._output = os.path.join(home,'.local','share','mapXplore')
            self._results["output"] = self._output

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

    def save(self, content, format, name=None):
        self._create_directory(self._output)
        if name is None:
            current_date = datetime.now()
            format_date = current_date.strftime("%Y%m%d%H%M%S")
            name = f"{format_date}.{format}"
        
        self._write_content(content, os.path.join(self._results["output"], name))
    
