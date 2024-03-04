import cmd2
from cmd2 import CommandSet, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser
from utils.ansiprint import AnsiPrint
from config.settings import Settings
from middle.running import Running, QueryType
from console.modules.argumentsManager import ArgumentsManager
from utils.crypto.hashes import Hashes
import i18n.locale as locale

@with_default_category('Query Category')
class QueryCommandSet(CommandSet, ArgumentsManager):
    def __init__(self, args) -> None:
        super().__init__()
        if args is not None:
            if args.config:
                Settings.load_settings(args.config)
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
        # if len(arg.arg_list)>=1:
        #     if arg.arg_list[0] not in self._filter_options:
        #         option = 'values'
        #         value= ' '.join(arg.arg_list)
                
        #     else:
        #         option, value = self._get_arguments(arg, 1)
      

        # hash_type = None
        # if option is not None:
        #     if option in Settings.allow_hashes:
        #         hash_type = option
        #     elif option not in self._filter_options:
        #         value = option
        #         option = 'values'
            
        #     options = []
        #     if option == 'all':
        #         options = self._filter_options
        #     else:
        #         options.append(option)
        hash_type = None
        if len(arg.arg_list)==1:
            query_option = QueryType.VALUES
            value = arg.arg_list[0]
        elif len(arg.arg_list) > 1:
            option = arg.arg_list[0]
            value = arg.arg_list[1]
            if option == 'tables':
                query_option = QueryType.TABLES
            elif option == 'columns':
                query_option = QueryType.COLUMNS
            elif option in Settings.allow_hashes:
                query_option = QueryType.VALUES
                hash_type = option

        results = self._core.run(query_option, value, hash_type)
        if results:
            self._results.append(results)
            
            # elif opt == 'values':
                
            # elif opt in :
            #     query_option = QueryType.VALUES
            # else:
            #     AnsiPrint.print_error(f"Criterial not found {option}")
                
               