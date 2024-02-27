class Connection:
    def __init__(self, **kwargs) -> None:
        for key, item in kwargs.items():
            setattr(self, key, item)
    

    server:str=""
    username:str=""
    password:str=""
    database=""
    delimiter=""
    table=""
    recreate=False
    dbms=""
