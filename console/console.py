from utils.ansiprint import AnsiPrint
import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from config.settings import Settings
from console.modules.configCommand import ConfigCommandSet
from console.modules.queryCommand import QueryCommandSet
from console.modules.importCommand import ImportCommand
from middle.running import Running
import i18n.locale  as locale



class SearchConsole(cmd2.Cmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, allow_cli_args=False)
        self._default_prompt = 'mapXplore> '
        self._sqlmap = Settings.setting["sqlmap"]
        self.prompt = self._default_prompt
        self.register_postcmd_hook(self._postcmd)
        self.debug=True
        self._results = []
        self._core = Running()
        self._filter_options = Settings.filter_options
        self._args = args
        self._commands = []
    

    use_parser = Cmd2ArgumentParser(add_help="")
    
    subparser = use_parser.add_subparsers(dest='module')

    import_parser = subparser.add_parser('import', help='Import module')
    config_parser = subparser.add_parser('config', help='Config Module')

    config_parser.add_argument('section',choices=list(Settings.setting.keys()))

    import_parser.add_argument('--database', help="Database to be imported from sqlmap")
    import_parser.add_argument('--input',help="Path of the site extracted from sqlmap (before /dump)")
    import_parser.add_argument('--delimiter', help="sqlmap Output File Delimiter")
    import_parser.add_argument('--dbms', choices=['postgres','sqlite'], help="Set DBMS to import data")
    import_parser.add_argument('--recreate', help="Set if destroy previous databases instance", action='store_true')
    

    #use_parser.add_argument("module", choices=['import','config'])

    def _postcmd(self, data: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        self.prompt = self._default_prompt
        for command in self._commands:
            self.prompt+=command["module"]+"> "

        return data
    def do_quit(self, arg):
        return True
    
    """
    Enables importing the results obtained from running sqlmap to a PostgreSQL or MongoDB database, facilitating searches with greater ease
    """
    def do_back(self, args):
        if len(self._commands) > 0:
            command = self._commands.pop()
            self.unregister_command_set(command["command"])


    @with_argparser(use_parser)
    #@cmd2.as_subcommand_to('use','use', parser=use_parser)
    def do_use(self, arg):
        module = None
        #command_set = [command for command in self._commands if command['module']==arg.module]
        for command in self._commands:
            self.do_back(command["module"])

        if arg.module == 'import':
            
            if arg.input is None and self._sqlmap["input"]=='':
                AnsiPrint.print_info("You need specified input folder")
            
            module = ImportCommand(arg)
        elif arg.module == 'config':
            module = ConfigCommandSet(arg, section=arg.section)

        if module is not None:
            self._commands.append({"module":arg.module, "command":module, "args": arg})
            self.register_command_set(module)


def main():
    parser = Cmd2ArgumentParser()
    parser.add_argument('-s','--host', required=False, help='Postgress server IP/Name')
    parser.add_argument('-u', '--username', required=False, help='Username of the database server')
    parser.add_argument('-p', '--password', required=False, help='Username of the database server')
    parser.add_argument('-D', '--database', required=False, help='Specific database to search')
    parser.add_argument('--dbms', choices=['postgres','mongo','sqlite'],default='mongo')
    args = parser.parse_args()
    
    QueryCommandSet()
    app = SearchConsole()
    app.cmdloop()
