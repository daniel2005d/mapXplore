from database.connection import Connection
from utils.utils import Util
from utils.ansiprint import AnsiPrint
from utils.colors import Color
import cmd2
from cmd2 import Cmd2ArgumentParser
from dbConnector import DbConnector
from model.result import Result
from config.settings import Settings
from utils.savemanager import SaveManager

class SearchConsole(cmd2.Cmd):
    def __init__(self) -> None:
        super().__init__(allow_cli_args=False)
        self.prompt = 'mapXplore> '
        self.debug=True
        self._results = []
        self._filter_options = Settings.filter_options
        self._output_settings = Settings.setting["Results"]
        self._export_manager = SaveManager()
        
        delattr(cmd2.Cmd, 'do_set')
        
    
    def set_config(self, **kwargs):
        for key, value in kwargs.items():
            Settings.setting["Database"][key]=value
        
        config = Settings.setting["Database"]
        db = DbConnector(database=config["database"], host=config["host"], 
                         username=config["username"], password=config["password"], 
                         dbtype=config["dbtype"])
        self._cursor = db._createDBEngine()
    
    def _print_results(self):
        if len(self._results)==0:
            AnsiPrint.print_info("There are no results yet")
        else:
            for r in self._results:
                AnsiPrint.printResult(r)
    
    def get_arguments(self, args, length=2):
        arguments = args.arg_list
        value,option = None, None
        for index, argv in enumerate(arguments):
            if index == 0:
                option = argv
            else:
                value = '' if value is None else value
                value+= " " + argv

        return option, value.lstrip() if value is not None else None
    
    def _filter_by_value(self, value_to_find):
        queries = self._cursor.create_query_to_all_values(value_to_find, Settings.setting["Query"]["logical_operator"])
        found = False
        for qry in queries:
            table_name = qry["tablename"]
            results = self.run_query(qry["sentence"], value_to_find)
            if results.length > 0:
                found = True
                self._results.append(results)
                AnsiPrint.print(f"Table Name: [bold][chartreuse_1]{table_name}[reset]")
                AnsiPrint.printResult(results)
        if found == False:
            AnsiPrint.print_info(f"Not results found for [yellow]{value_to_find}[reset]")
            

    """
    Run the query and highlight the text that matches.
    """
    def run_query(self, sentence, value_to_hight_light):
        result = self._cursor.execute_query(sentence)
        information = Result()
        if result is not None:
            
            for col in result[0].keys():
                information.headers.append(col)

            for row in result:
                columns = []
                for key in row:
                    column_value = str(row[key])
                    data,format = Util.is_base64(column_value)
                    column_text, formatted = Color.highlight_text(column_value, value_to_hight_light)
                    if data is not None:
                        if len(column_text) > 500:

                            truncated_text = Color.format(f"{column_text[0:500]}[cyan][{format if format is not None else 'Truncated...'}][reset]")
                            columns.append(truncated_text)

                    if data is not None and format is not None:
                        if self._output_settings["savefiles"]:
                            AnsiPrint.print_info(f"Saving file of the [yellow]{key}[end] column")
                            self._export_manager.save(data, format)
                    else:
                        columns.append(column_text)

                information.rows.append(columns)

        return information

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

    def do_set(self, args):
        if len(args.arg_list) != 3:
            AnsiPrint.print_error("")
        else:
            # option, value = self.get_arguments(args)
            section = args.arg_list[0]
            option = args.arg_list[1]
            value = args.arg_list[2]

            if section in Settings.setting:
                if option in Settings.setting[section]:
                    Settings.setting[section][option]=value
                    self.set_config()
            else:
                Util.print_error(f'Argument {option} {value} is not recognized')
                return False
    
    def do_show(self, arg):
        option, value = self.get_arguments(arg, 1)
        if option is not None:
            if option=='results':
                self._print_results()
            elif value is None:
                for section in Settings.setting:
                    AnsiPrint.print(f"[green]{section}[reset]")
                    for option in Settings.setting[section]:
                        AnsiPrint.print(f"\t[bold]{option}[reset]: {Settings.setting[section][option]}")
            elif value not in Settings.setting:
                AnsiPrint.print_error("The configuration option does not exist")
            else:

                for section in Settings.setting[value]:
                    AnsiPrint.print(f"\t[bold]{section}:[reset]{Settings.setting[value][section]}")


    def do_quit(self, arg):
        return True
    
    def complete_search(self, text, line, begidx, endidx):
        return self._run_completions(self._filter_options, text)

    def complete_set(self, text, line, begidx, endidx):
        return self._run_completions(line)

    def do_search(self, arg):
        option, value = self.get_arguments(arg, 1)
        if option is not None:
            if option not in self._filter_options:
                value = option
                option = 'values'
            
            options = []
            if option == 'all':
                options = self._filter_options
            else:
                options.append(option)

            for opt in options:
                results = None
                if opt == 'tables':
                    results = self._cursor.search_tables(value)
                if opt == 'columns':
                    results = self._cursor.search_columns(value)
                if opt == 'values':
                    self._filter_by_value(value)
                
                if results is not None:
                    self._results.append(results)
                    AnsiPrint.printResult(results)
            
def main():
    parser = Cmd2ArgumentParser()
    parser.add_argument('-s','--host', required=False, help='Postgress server IP/Name')
    parser.add_argument('-u', '--username', required=False, help='Username of the database server')
    parser.add_argument('-p', '--password', required=False, help='Username of the database server')
    parser.add_argument('-D', '--database', required=True, help='Specific database to search')
    parser.add_argument('--dbtype', choices=['postgres','mongo'],default='postgress')
    
    args= parser.parse_args()

    search = SearchConsole()
    search.set_config(host=args.host, username=args.username, password=args.password, database=args.database, dbtype=args.dbtype)
    search.cmdloop()
