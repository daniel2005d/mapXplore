import i18n.locale as locale
class MapXploreException(Exception):
    def __init__(self, *args: object, message_key=None,message=None, isError=True) -> None:
        super().__init__(*args)
        self._message_key = message_key
        self._message = message
        self._isError = isError
    
    def __str__(self) -> str:
        message = None
        if self._message is None:
            if self._message_key:
                message = locale.get("errors."+self._message_key)
        else:
            message = self._message
            
        return message

    @property
    def isError(self)->bool:
        return self._isError
        