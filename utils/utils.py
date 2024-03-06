from colored import Style, fore, back
import hashlib
from base64 import b64decode
import magic
import mimetypes
import os

class Util:

    @staticmethod
    def check_file(file_name:str)->bool:
        if not os.path.exists(file_name) or not os.path.isfile(file_name):
            return False
        
        return True
    
    @staticmethod
    def is_readable(content:bytes)->bool:
        allowed_bytes = set(range(32, 127)) | {10,13} | {241,243,250}
        
        for byte in content:
            if byte not in allowed_bytes:
                return False
        return True
    
    def get_readable_content(content:bytes)->str:
        text = ""
        allowed_bytes = set(range(32, 127)) | {10,13} | {241,243,250}
        
        for byte in content:
            if byte not in allowed_bytes:
                text+=" "
            else:
                text+=chr(byte)
        
        return text


    @staticmethod
    def try_convert_b64(text)->tuple[bytes,str]:
        b64bytes = b64decode(text)
        data_format = Util.get_data_type(text)
        return b64bytes,data_format
    
    @staticmethod
    def get_data_type(content:bytes)->str:
        decoded_bytes = b64decode(content[:100])
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(decoded_bytes)
        return mimetypes.guess_extension(file_type).replace('.','')
    
    @staticmethod
    def get_filename(filename:str)->str:
        full_name = os.path.basename(filename)
        name = os.path.splitext(full_name)[0]
        return name
    
    @staticmethod
    def decode(text:str)->str:
        decoded = text
        try:
            if text is None:
                return None
            if not text.isdigit():
                decoded = text.encode('latin').decode('unicode_escape')
        except:
            pass
        
        return decoded

class Hashing:
    @staticmethod
    def get_md5(text)->str:
        if isinstance(text, bytes):
            return hashlib.md5(text).hexdigest()
        else:
            return hashlib.md5(text.encode()).hexdigest()

class CastDB:
    def cast_column(column_name, data_type):
        if data_type not in ["character","text", "character varying"]:
            return f"{column_name}::varchar(255)"
        else:
            return column_name