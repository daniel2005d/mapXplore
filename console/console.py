from utils.ansiprint import AnsiPrint
import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from config.settings import Settings
from console.modules.configCommand import ConfigCommandSet
from console.modules.queryCommand import QueryCommandSet
from console.modules.importCommand import ImportCommand
from middle.running import Running
import i18n.locale  as locale



class MainConsole(cmd2.Cmd):
    """Enables importing the results obtained from running sqlmap to a PostgreSQL
     or sqlite database, facilitating searches with greater ease
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, allow_cli_args=False, auto_load_commands=False)
        self._default_prompt = 'mapXplore # '
        self._sqlmap = Settings.setting["sqlmap"]
        self.prompt = self._default_prompt
        self.register_postcmd_hook(self._postcmd)
        self.debug=True
        self._results = []
        self._core = Running()
        self._filter_options = Settings.filter_options
        self._args = args
        self._commands = []
    

    use_parser = Cmd2ArgumentParser(add_help=locale.get("help_import"))
    
    subparser = use_parser.add_subparsers(dest='module')

    import_parser = subparser.add_parser('import', help='Import module')
    config_parser = subparser.add_parser('config', help='Config Module')

    config_parser.add_argument('section',choices=list(Settings.setting.keys()), default=None, nargs='?')

    import_parser.add_argument('--database', help="Database to be imported from sqlmap")
    import_parser.add_argument('--input',help="Path of the site extracted from sqlmap (before /dump)")
    import_parser.add_argument('--delimiter', help="sqlmap Output File Delimiter")
    import_parser.add_argument('--dbms', choices=['postgres','sqlite'], help="Set DBMS to import data")
    import_parser.add_argument('--recreate', help="Set if destroy previous databases instance", action='store_true')
    

    def _load_module(self, arg=None) -> None:
        module = None
        for command in self._commands:
            self.do_back(command["module"])

        if arg  is None:
            module = QueryCommandSet()
        elif arg.module == 'import':
            module = ImportCommand(arg)
        elif arg.module == 'config':
            module = ConfigCommandSet(arg, section=arg.section)

        if module is not None:
            self._commands.append({"module":arg.module if hasattr(arg,'module') else 'main', "command":module, "args": arg})
            self.register_command_set(module)

    def _postcmd(self, data: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        self.prompt = self._default_prompt
        for command in self._commands:
            self.prompt+=command["module"]+"> "

        if len(self._commands)== 0:
            self._load_module(None)
        return data
    
    def do_quit(self, arg):
        return True
    
    
    def do_back(self, args):
        if len(self._commands) > 0:
            command = self._commands.pop()
            self.unregister_command_set(command["command"])
        
        

    @with_argparser(use_parser)
    def do_use(self, arg):
        self._load_module(arg)

def main():
    
    app = MainConsole()
    app._load_module(None)
    app.cmdloop()
