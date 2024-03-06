import cmd2
from cmd2 import CommandSet, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser
from config.settings import Settings, SqlMapSetting
from middle.data_importer import DataImporter
from utils.ansiprint import AnsiPrint

@with_default_category('Import Category')
class ImportCommand(CommandSet):
    def __init__(self) -> None:
        super().__init__()
        self._core = DataImporter()
        if hasattr(cmd2.Cmd,'do_set'):
            delattr(cmd2.Cmd, 'do_set')
        
        if  SqlMapSetting().file_input == '':
            AnsiPrint.print_locale("import.input_required")
        
    set_parser = Cmd2ArgumentParser(add_help="")
    set_parser.add_argument('option', choices=list(SqlMapSetting().keys))
    
    
    def do_run(self, arg):
        if SqlMapSetting().file_input is None:
            AnsiPrint.print_error("You must specify the directory where the data downloaded by sqlmap is located.")
        else:
            self._core.start()
    
    def do_options(self, arg):
        AnsiPrint.printSetting(SqlMapSetting().key_name)
    
    @with_argparser(set_parser)
    def do_set(self, arg):
        pass
        
