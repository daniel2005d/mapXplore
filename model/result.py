class Result:
    def __init__(self, **kwargs) -> None:
        self.headers = []
        self.rows = []
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def length(self) -> int:
        return len(self.rows)

    