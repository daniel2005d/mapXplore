from utils.ansiprint import AnsiPrint
import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from config.settings import Settings
from console.modules.configCommand import ConfigCommandSet
from console.modules.queryCommand import QueryCommandSet
from console.modules.importCommand import ImportCommand
from middle.running import Running




class SearchConsole(cmd2.Cmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, allow_cli_args=False)
        self._default_prompt = 'mapXplore> '
        self.prompt = self._default_prompt
        self.register_postcmd_hook(self._postcmd)
        self.debug=True
        self._results = []
        self._core = Running()
        self._filter_options = Settings.filter_options
        self._args = args
        self._commands = []
    

    import_parser = Cmd2ArgumentParser()
    import_parser.add_argument('--input',help="Path of the site extracted from sqlmap (before /dump)")
    import_parser.add_argument('--delimiter', help="sqlmap Output File Delimiter")
    import_parser.add_argument('--database', help="Database to be imported from sqlmap")
    import_parser.add_argument('--recreate', help="Set if destroy previous databases instance", action='store_true')
    import_parser.add_argument("module", choices=['import'])

    def _postcmd(self, data: cmd2.plugin.PostcommandData) -> cmd2.plugin.PostcommandData:
        self.prompt = self._default_prompt
        for command in self._commands:
            self.prompt+=command["module"]+"> "

        return data
    def do_quit(self, arg):
        return True
    
    def do_back(self, args):
        if len(self._commands) > 0:
            command = self._commands.pop()
            self.unregister_command_set(command["command"])

    @with_argparser(import_parser)
    @cmd2.as_subcommand_to('use', 'import', import_parser)
    def do_use(self, arg):
        if arg.module == 'import':
            command_set = [command for command in self._commands if command['module']==arg[0]]
            if len(command_set)==0:
                if arg.input is None:
                    AnsiPrint.print_info("You need specified input folder")
                
                import_module = ImportCommand(arg)
                self._commands.append({"module":arg.module, "command":import_module})
                self.register_command_set(import_module)


def main():
    parser = Cmd2ArgumentParser()
    parser.add_argument('-s','--host', required=True, help='Postgress server IP/Name')
    parser.add_argument('-u', '--username', required=False, help='Username of the database server')
    parser.add_argument('-p', '--password', required=False, help='Username of the database server')
    parser.add_argument('-D', '--database', required=False, help='Specific database to search')
    parser.add_argument('--dbms', choices=['postgres','mongo'],default='mongo')
    args = parser.parse_args()
    commands = ConfigCommandSet(args)
    QueryCommandSet()
    
    app = SearchConsole(command_sets=[commands])
    app.cmdloop()
