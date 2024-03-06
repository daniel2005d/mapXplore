import sys
import shutil
from model.result import Result
from utils.colors import Color
from cmd2 import ansi, EightBitBg, RgbFg
from config.settings import Settings
from config.settings import GeneralSetting
import i18n.locale as locale

from typing import (
    Any,
    List,
)
from cmd2.table_creator import (
    AlternatingTable,
    BorderedTable,
    Column,
    HorizontalAlignment,
    SimpleTable,
)


class AnsiPrint:

    @staticmethod
    def printSetting(section:str):
        columns: List[Column] = list()
        data_list: List[List[Any]] = list()
        option = Settings.setting[section]
        
        for key in option:
            columns.append(Column(ansi.style(key, bold=True,italic=True, bg=EightBitBg.GRAY_53), width=30))
        
        rows = []
        for index, value in enumerate(option):
            setting_value = option[value]
            rows.append(setting_value)
            columns[index].width = max(columns[index].width,len(str(setting_value)))
        
        data_list.append(rows)

        
        st = SimpleTable(columns)
        table = st.generate_table(data_list)
        print(table)

    @staticmethod
    def printResult(result:Result):
        if result is not None:
            width = shutil.get_terminal_size().columns
            columns: List[Column] = list()
            data_list: List[List[Any]] = list()
            for header in result.headers:
                column_width = int(width/len(result.headers))
                if column_width > 10:
                    column_width-= 5

                columns.append(Column(ansi.style(header, bold=True,italic=True, bg=EightBitBg.GRAY_53), width=column_width))
            
            if result.formatted_len > 0:
                for row in result.formatted_rows:
                    data_list.append(row)
            else:
                for row in result.rows:
                    data_list.append(row)
            
            bt = BorderedTable(columns)
            table = bt.generate_table(data_list)
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
        AnsiPrint.print_debug()
            

    @staticmethod
    def print_debug(exception:Exception=None):
        if GeneralSetting().isDebug:
            message = ""
            if exception is None:
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

    
    
