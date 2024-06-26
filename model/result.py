from enum import Enum

class Result:
    def __init__(self, **kwargs) -> None:
        self.table_name=None
        self.headers = []
        self.rows = []
        self.formatted_rows = []
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def length(self) -> int:
        return len(self.rows)

    @property
    def formatted_len(self)->int:
        return len(self.formatted_rows)

    def append(self, rows)->None:
        self.rows.append(rows)
    
    def get_column(self, index:int=None, column_name:str=None)->str:
        if index is not None:
            return self.headers[index]
        elif column_name is not None:
            return self.headers.index(column_name)

    
    def contains_header(self, name:str)->bool:
        return name in self.headers


class QueryType(Enum):
    NONE = 0
    TABLES = 1
    COLUMNS = 2
    VALUES = 3
    ALL = 4

class QueryResult:
    def __init__(self, **kwargs) -> str:
        self.criterial:QueryType = None
        self.results:Result = None
        self.value:str = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def length(self) -> int:
        return self.results.length
    
    def append(self, rows:list[Result])->None:
        for row in rows.rows:
            self.results.rows.append(row)

