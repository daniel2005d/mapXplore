class Base64File:
    def __init__(self, **kwargs) -> None:
        self.extension = None
        self.filename = None
        self.content = None
        for argv in kwargs.items():
            setattr(self, argv, kwargs[argv])
