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

    