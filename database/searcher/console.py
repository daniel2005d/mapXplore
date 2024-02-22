from database.connection import Connection
from utils import Util
import cmd2
import re
from stdout.colors import Color
from cmd2 import Cmd2ArgumentParser
from dbConnector import DbConnector
from model.result import Result
from stdout.ansiprint import AnsiPrint

class SearchConsole(cmd2.Cmd):
    def __init__(self) -> None:
        super().__init__(allow_cli_args=False)
        self.prompt = 'mapXplore>'
        self.debug=True
        self._objects = {}
        self._config = {
            "operator":"or",
            "elapsed":False,
            "database":"",
            "host":"",
            "username":"",
            "password":"",
            "dbtype":"",
        }
        self._filter_options = ['tables','columns','values','all']
        delattr(cmd2.Cmd, 'do_set')
        
    
    def set_config(self, **kwargs):
        for key, value in kwargs.items():
            self._config[key]=value

        db = DbConnector(database=self._config["database"], host=self._config["host"], 
                         username=self._config["username"], password=self._config["password"], 
                         dbtype=self._config["dbtype"])
        self._cursor = db._createDBEngine()
    
    
    
    def print_information(self):
        

        print(Color.format(f"=== [bold]Configuration[reset] ===="))
        for config in self._config:
            print(Color.format(f"[cyan]{config}: [green]{self._config[config]}[reset]"))
    
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
    
    def _print_objects(self, option:str):
        if option in self._objects:
            value = self._objects[option]
            print(value)
        else:
            Util.print_important(f"It don't have {option}")
        
    
    def _filter_by_value(self, value_to_find):
        queries = self._cursor.create_query_to_all_values(value_to_find, self._config["operator"])
        for qry in queries:
            table_name = qry["tablename"]
            results = self.run_query(qry["sentence"], value_to_find)
            if results.length > 0:
                AnsiPrint.printResult(results)


    def run_query(self, sentence, value_to_hight_light):
        result = self._cursor.execute_query(sentence)
        information = Result()
        if result is not None:
            
            for col in result[0].keys():
                information.headers.append(col)

            for row in result:
                columns = []
                for key in row:
                    column_text, formatted = Color.format_string(row[key], value_to_hight_light)
                    columns.append(column_text)
                information.rows.append(columns)

        return information

    def _run_completions(self, options, text):
        completions=[]
        possible_completions = options
        for word in possible_completions:
            if word.startswith(text):
                completions.append(word)
        return completions    

    def do_set(self, args):
        option, value = self.get_arguments(args)
        if option is not None:
            if option in self._config:
                self._config[option]=value
                self.set_config()
            else:
                Util.print_error(f'Argument {option} {value} is not recognized')
                return False
    
    def do_show(self, arg):
        option, _ = self.get_arguments(arg, 1)
        if option is not None:
            if option == 'config':
                self.print_information()
            else:
                self._print_objects(option)

    
    def do_quit(self, arg):
        return True
    
    def complete_search(self, text, line, begidx, endidx):
        return self._run_completions(self._filter_options, text)

    def complete_set(self, text, line, begidx, endidx):
        return self._run_completions(self._config, text)

    def do_search(self, arg):
        option, value = self.get_arguments(arg, 1)
        if option not in self._filter_options:
            value = option
            option = 'values'
        
        options = []
        if option == 'all':
            options = self._filter_options
        else:
            options.append(option)

        for opt in options:
            if opt == 'tables':
                tables = self._cursor.search_tables(value)
                AnsiPrint.printResult(tables)
            
            if opt == 'columns':
                columns = self._cursor.search_columns(value)
                AnsiPrint.printResult(columns)
            if opt == 'values':
                values = self._filter_by_value(value)
            
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
