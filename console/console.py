import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from config.settings import Settings
from console.modules.configCommand import ConfigCommandSet
from console.modules.queryCommand import QueryCommandSet
from console.modules.importCommand import ImportCommand
import i18n.locale  as locale
from middle.data_operation import DataManager
from utils.colors import Color


class MainConsole(cmd2.Cmd):
    """Enables importing the results obtained from running sqlmap to a PostgreSQL
     or sqlite database, facilitating searches with greater ease
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, allow_cli_args=False, auto_load_commands=False)
        cmd = Color.format("[yellow]>[blue]>[red]>[reset]")
        prompt = Color.format("[yellow]mapXp[blue]lo[red]re[reset]")
        self._default_prompt = f'{prompt} {cmd} '
        
        self.prompt = self._default_prompt
        self.register_postcmd_hook(self._postcmd)
        self.debug=True
        self._results = []
        self._core = DataManager()
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
    

    def _load_module(self, arg=None) -> None:
        module = None
        for command in self._commands:
            self.do_back(command["module"])

        if not hasattr(arg, 'module'):
            module = QueryCommandSet(arg)
        elif arg.module == 'import':
            module = ImportCommand()
        elif arg.module == 'config':
            module = ConfigCommandSet(arg, section=arg.section)

        if module is not None:
            self._commands.append({"module":arg.module if hasattr(arg,'module') else 'main', "command":module, "args": arg})
            self.register_command_set(module)

    def _postcmd(self, data: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        self.prompt = self._default_prompt
        for command in self._commands:
            self.prompt+=command["module"]+Color.format("[green]>[reset] ")

        if len(self._commands)== 0:
            self._load_module(None)
        return data
    
    def do_quit(self, arg):
        """Exit of the application
        """
        return True
    
    
    def do_back(self, args):
        """Return to main module
        """
        if len(self._commands) > 0:
            command = self._commands.pop()
            if hasattr(command["command"],"close_connection"):
                command["command"].close_connection()
                
            self.unregister_command_set(command["command"])

    @with_argparser(use_parser)
    def do_use(self, arg):
        """"Load config or import a module
        """
        self._load_module(arg)

def main(args):
    
    app = MainConsole()
    app._load_module(args)
    app.cmdloop()
