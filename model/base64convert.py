class Base64File:
    def __init__(self, **kwargs) -> None:
        self.extension = None
        self.filename = None
        self.content = None
        for key, value in kwargs.items():
            setattr(self, key, value)
