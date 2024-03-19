from tabulate import tabulate
from model.result import Result
from utils.colors import Color
from config.settings import Settings
from config.settings import GeneralSetting
import i18n.locale as locale

class AnsiPrint:

    @staticmethod
    def printSetting(section:str):
        
        title_message = locale.get("config.table_key_title")
        title_value = locale.get("config.table_value_title")
        data_list= []
        option = Settings.setting[section]
        
        for key in option:
            data_list.append([key, option[key]])

        table_format = "mixed_outline"
        table = tabulate(data_list, headers=[title_message, title_value], tablefmt=table_format)
        print(table)
        

    @staticmethod
    def printResult(result:Result):
        if result is not None:
            table = tabulate(result.rows, headers=result.headers, tablefmt="rounded_outline")
            print(table)
      
    @staticmethod
    def print(text:str, end:str='\r\n')->None:
        print(Color.format(text), end=end)

    @staticmethod
    def print_info(text:str)->None:
        AnsiPrint.print(f"[yellow][!][bold] {text}[reset]")
    
    @staticmethod
    def print_error(text:str)->None:
        AnsiPrint.print(f"[red][-][bold] {text}[reset]")
        AnsiPrint.print_debug(text)
            

    @staticmethod
    def print_debug(exception:Exception=None):
        if GeneralSetting().isDebug:
            message = ""
            if isinstance(exception,Exception):
                import traceback
                traceback.print_exc()
                # exc_type, exc_value, exc_traceback = sys.exc_info()
                # if exc_traceback:
                #     message = f"{exc_value} {exc_traceback}"
            else:
                message = str(exception)
                AnsiPrint.print(f"[bold][yellow][debug][reset] [yellow]{message} [reset]")
            
    @staticmethod
    def print_success(text:str)->None:
        AnsiPrint.print(f"[green][+][bold] {text}[reset]")
    
    @staticmethod
    def print_locale(sectionkey:str,end='\r\n', **kwargs)->None:
        text = locale.get(sectionkey)
        AnsiPrint.print(text.format(**kwargs), end=end)

    
    
