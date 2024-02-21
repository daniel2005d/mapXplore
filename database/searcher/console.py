from database.connection import Connection
from utils import Util
import cmd2
import re
from colors import Color
from cmd2 import Cmd2ArgumentParser, with_argparser
from dbConnector import DbConnector


class SearchConsole(cmd2.Cmd):
    def __init__(self) -> None:
        super().__init__()
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
            if index == 1:
                value = argv

        return option, value
    
    def _print_objects(self, option:str):
        if option in self._objects:
            value = self._objects[option]
            print(value)
        else:
            Util.print_important(f"It don't have {option}")
    
    def _filter_by_value(self, value_to_find):
        queries = self._cursor.create_query_to_all_values(value_to_find, self._config["operator"])
        for qry in queries:
            results = self.run_query(qry["sentence"])
            tablename = qry["tablename"]
            
            if results:
                print(Color.format(f"Table [white][bold]{tablename}[reset]"))
                for row in results:
                    for column in row:
                        row_value = str(row[column])
                        matches = re.search(value_to_find, row_value, flags=re.IGNORECASE)
                        if matches:
                            start = matches.start()
                            end = matches.end()
                            hight_light = Color.format(f"[blue][bold]{column}[reset]=>{row_value[:start]}[red]{row_value[start:end]}[reset]{row_value[end:]}")
                            print(hight_light)
                   
                        

    def run_query(self, sentence):
        result = self._cursor.execute_query(sentence)
        return result

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
                self._objects["tables"]=tables
            if opt == 'columns':
                columns = self._cursor.search_columns(value)
                self._objects["columns"]=columns
            if opt == 'values':
                self._filter_by_value(value)
                
            self._print_objects(opt)


def main():
    parser = Cmd2ArgumentParser()
    # parser = argparse.ArgumentParser()
    parser.add_argument('-s','--host', required=False, help='Postgress server IP/Name')
    parser.add_argument('-u', '--username', required=False, help='Username of the database server')
    parser.add_argument('-p', '--password', required=False, help='Username of the database server')
    parser.add_argument('-D', '--database', required=True, help='Specific database to search')
    parser.add_argument('--dbtype', choices=['postgres','mongo'],default='postgress')
    # parser.add_argument('value',  help='Value to filter')
    #args = parser.parse_args()
    args= parser.parse_args()

    search = SearchConsole()
    search.set_config(host=args.host, username=args.username, password=args.password, database=args.database, dbtype=args.dbtype)
    search.cmdloop()
