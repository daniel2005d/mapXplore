from utils.ansiprint import AnsiPrint
import cmd2
from cmd2 import Cmd2ArgumentParser
from config.settings import Settings
from console.modules.configCommand import ConfigCommandSet
from console.modules.queryCommand import QueryCommandSet
from middle.running import Running, QueryType


class SearchConsole(cmd2.Cmd):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, allow_cli_args=False)
        self.prompt = 'mapXplore> '
        self.debug=True
        self._results = []
        self._core = Running()
        self._filter_options = Settings.filter_options
    
    
    def _print_results(self):
        if len(self._results)==0:
            AnsiPrint.print_info("There are no results yet")
        else:
            for r in self._results:
                AnsiPrint.printResult(r)
    
      
    def _run_completions(self, text):
        line = text.strip()
        text = line.replace('set','').strip()
        completions=[]
        possible_completions=[]
        if text in Settings.setting:
            possible_completions=Settings.setting[text]
            text = ''
        else:
            possible_completions = Settings.setting
        for word in possible_completions:
            if word.startswith(text):
                completions.append(word)
        return completions    
    
    def do_quit(self, arg):
        return True
    
    def complete_search(self, text, line, begidx, endidx):
        return self._run_completions(text)


def main():
    parser = Cmd2ArgumentParser()
    parser.add_argument('-s','--host', required=False, help='Postgress server IP/Name')
    parser.add_argument('-u', '--username', required=False, help='Username of the database server')
    parser.add_argument('-p', '--password', required=False, help='Username of the database server')
    parser.add_argument('-D', '--database', required=True, help='Specific database to search')
    parser.add_argument('--dbtype', choices=['postgres','mongo'],default='postgress')
    
    args= parser.parse_args()
    commands = ConfigCommandSet(args)
    c = QueryCommandSet()
    search = SearchConsole(command_sets=[commands])
    search.cmdloop()
