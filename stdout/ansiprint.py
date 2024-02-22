from model.result import Result
import shutil

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
        width = shutil.get_terminal_size().columns
        columns: List[Column] = list()
        data_list: List[List[Any]] = list()
        for header in result.headers:
            columns.append(Column(header, width=int(width/len(result.headers))))
        
        for row in result.rows:
            data_list.append(row)
        
        bt = BorderedTable(columns)
        table = bt.generate_table(data_list)
        print(table)
    
    
