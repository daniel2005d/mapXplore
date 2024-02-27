import cmd2
from cmd2 import CommandSet, with_default_category
from config.settings import Settings
from middle.process import Import
from utils.ansiprint import AnsiPrint

@with_default_category('Import Category')
class ImportCommand(CommandSet):
    def __init__(self, args) -> None:
        super().__init__()
        self._core = Import(args)
        
    
    def do_run(self, arg):
        if Settings.setting["sqlmap"]["input"] is None:
            AnsiPrint.print_error("You must specify the directory where the data downloaded by sqlmap is located.")
        else:
            self._core.start()
