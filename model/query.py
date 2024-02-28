class Query:
    def __init__(self, **kwargs) -> None:
        self._sentence = None
        self._word = None
        self._tablename = None
        for arg in kwargs.keys():
            setattr(self, f"_{arg}", kwargs[arg])
    
    @property
    def sentence(self):
        return self._sentence
    
    @property
    def word(self):
        return self._word
    
    @property
    def tablename(self):
        return self._tablename