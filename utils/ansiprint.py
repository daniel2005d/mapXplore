from model.result import Result
from utils.colors import Color
import shutil
from cmd2 import ansi, EightBitBg, RgbFg

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
    def print(text:str)->None:
        print(Color.format(text))

    @staticmethod
    def print_info(text:str)->None:
        AnsiPrint.print(f"[yellow][!][bold] {text}[reset]")
    
    @staticmethod
    def print_error(text:str)->None:
        AnsiPrint.print(f"[red][-][bold] {text}[reset]")
    
    @staticmethod
    def print_success(text:str)->None:
        AnsiPrint.print(f"[green][+][bold] {text}[reset]")

    
    
