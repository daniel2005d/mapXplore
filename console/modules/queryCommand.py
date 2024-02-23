import cmd2
from cmd2 import CommandSet, with_default_category
from utils.ansiprint import AnsiPrint
from config.settings import Settings
from middle.running import Running, QueryType
from console.modules.argumentsManager import ArgumentsManager


@with_default_category('Query Category')
class QueryCommandSet(CommandSet, ArgumentsManager):
    def __init__(self) -> None:
        super().__init__()
        self._filter_options = Settings.filter_options
        self._core = Running()
    
    def do_search(self, arg):
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
                
                self._core.run(query_option, value, hash_type)