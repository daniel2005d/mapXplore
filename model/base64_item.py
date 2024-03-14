class Base64Item:
    def __init__(self, **kwargs) -> None:
        self.original_text:str = None
        self.fixed:str = None
        self.content:bytes=None
        for key, value in kwargs.items():
            setattr(self, key, value)