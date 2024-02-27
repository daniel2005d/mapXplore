import cmd2
from cmd2 import CommandSet, with_default_category
from utils.ansiprint import AnsiPrint
from config.settings import Settings
from middle.running import Running, QueryType
from console.modules.argumentsManager import ArgumentsManager
from utils.crypto.hashes import Hashes
from utils.colors import Color

@with_default_category('Query Category')
class QueryCommandSet(CommandSet, ArgumentsManager):
    def __init__(self) -> None:
        super().__init__()
        self._filter_options = Settings.filter_options
        self._result_options = Settings.setting["Results"]
        self._core = Running()
        self._results = []

    def complete_search(self, text, line, begidx, endidx):
        completions = []
        hashes = list(Hashes.get_available_algorithms())
        for hash in hashes:
            if hash.startswith(text):
                completions.append(hash)

        for item in Settings.filter_options:
            if item.startswith(text):
                completions.append(item)
        
        return completions
    
    def do_save(self, arg):
        format = arg.args if arg.args != '' else self._result_options["format"]
        if format in Settings.valid_format_files:
            self._core.export(format)
        else:
            AnsiPrint.print_error(f"[bold]{format}[reset] is not valid format")

    
    def do_search(self, arg):
        option = None
        value = None
        if len(arg.arg_list)>=1:
            if arg.arg_list[0] not in self._filter_options:
                option = 'values'
                value= ' '.join(arg.arg_list)
                
            else:
                option, value = self._get_arguments(arg, 1)

        hash_type = None
        if option is not None:
            if option in Settings.allow_hashes:
                hash_type = option
            elif option not in self._filter_options:
                value = option
                option = 'values'
            
            options = []
            if option == 'all':
                options = self._filter_options
            else:
                options.append(option)

            
            for opt in options:
                query_option = QueryType.NONE
                if opt == 'tables':
                    query_option = QueryType.TABLES
                elif opt == 'columns':
                    query_option = QueryType.COLUMNS
                elif opt == 'values':
                    query_option = QueryType.VALUES
                elif opt in Settings.allow_hashes:
                    query_option = QueryType.VALUES
                else:
                    AnsiPrint.print_error(f"Criterial not found {option}")
                
                results = self._core.run(query_option, value, hash_type)
                if results:
                    self._results.append(results)