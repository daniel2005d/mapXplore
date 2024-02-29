import cmd2
from cmd2 import CommandSet, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser
from config.settings import Settings
from middle.process import Import
from utils.ansiprint import AnsiPrint

@with_default_category('Import Category')
class ImportCommand(CommandSet):
    def __init__(self) -> None:
        super().__init__()
        self._core = Import()
        self._config_key = "sqlmap"
        self._setting = Settings.setting[self._config_key]
        if hasattr(cmd2.Cmd,'do_set'):
            delattr(cmd2.Cmd, 'do_set')
        
        if self._setting["input"] == '':
            AnsiPrint.print_locale("import.input_required")
        
    set_parser = Cmd2ArgumentParser(add_help="")
    set_parser.add_argument('option', choices=list(Settings.setting["sqlmap"].keys()))
    
    
    def do_run(self, arg):
        if Settings.setting["sqlmap"]["input"] is None:
            AnsiPrint.print_error("You must specify the directory where the data downloaded by sqlmap is located.")
        else:
            self._core.start()
    
    def do_options(self, arg):
        AnsiPrint.printSetting(self._config_key)
    
    @with_argparser(set_parser)
    def do_set(self, arg):
        pass
        
