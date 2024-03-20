import cmd2
from cmd2 import CommandSet, with_default_category
from cmd2 import Cmd2ArgumentParser,with_argparser
from config.settings import ResultSetting, Settings, SqlMapSetting
from console.modules.argumentsManager import ArgumentsManager
from middle.data_operation import DataManager, QueryType
from lib.crypto.hashes import Hashes
import i18n.locale as locale
from utils.ansiprint import AnsiPrint


@with_default_category('Query Category')
class QueryCommandSet(CommandSet, ArgumentsManager):
    def __init__(self, args) -> None:
        super().__init__()
        if args is not None:
            if args.config:
                Settings.load_settings(args.config)
        self._filter_options = Settings.filter_options
        self._config = ResultSetting()
        self._core = DataManager()
        self._remove_default_commands()
    
    def close_connection(self):
        if self._core:
            self._core.close()
        

    parser = Cmd2ArgumentParser(add_help="")
    subparser = parser.add_subparsers(dest='section', required=True)

    format_parser = subparser.add_parser('format')
    format_parser.add_argument('value', choices=Settings.valid_format_files)

    database_parser = subparser.add_parser('database')
    database_parser.add_argument('value')

    output_parser = subparser.add_parser('output')
    output_parser.add_argument('value')
    
    def _remove_default_commands(self):
        for command in Settings.get_default_commands():
            if hasattr(cmd2.Cmd, command):
                delattr(cmd2.Cmd, command)


    @with_argparser(parser)
    def do_set(self, arg):
        if arg.section != 'database':
            ResultSetting().set_value(arg.section,arg.value)
        else:
            SqlMapSetting().set_value(arg.section,arg.value)

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
    
    
    def do_clean(self, arg):
        self._core.clean()

    def do_save(self, arg):
        """Stores the queries performed in HTML or CSV formats
        """
        format = arg.args if arg.args != '' else self._config.format
        if format in Settings.valid_format_files:
            self._core.export(format)
        else:
            AnsiPrint.print_error(f"[bold]{format}[reset] is not valid format")
    
    def do_select(self, arg):
        self._core.select(arg)

    def do_tables(self, _):
        self._core.table_count_rows()
    
    def do_databases(self, _):
        self._core.databases()
    
    def do_columns(self, args):
        self._core.columns(args.args)


    def do_search(self, arg):
        """
        Facilitates searching for the imported information
        """
        query_option = QueryType.NONE
        option = None
        value = None
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
            else:
                query_option = QueryType.VALUES
                value = ' '.join(arg.arg_list)

        if query_option!= QueryType.NONE and value is not None:
            self._core.run(query_option, value, hash_type)
        else:
            AnsiPrint.print_locale("errors.no_value_to_search")
            