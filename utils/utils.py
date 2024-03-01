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
        allowed_bytes = set(range(32, 127)) | {10,13}
        allowed_bytes |= set(range(192, 256)) # Add Latin chars
        for byte in content:
            if byte not in allowed_bytes:
                return False
        return True

    @staticmethod
    def is_base64(text)->tuple[bytes,str]:
        invalid_b64_chars = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', ':', ';', '<', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
        try:
            if text.isdigit():
                return None,None
            elif any(char in invalid_b64_chars for char in text):
                return None,None
            elif len(text) % 4 != 0:
                return None, None

            data,mimetype = Util.try_convert_b64(text)
            if not Util.is_readable(data):
                return None, mimetype
            
            data = data.decode('latin')
            
            return data,mimetype
        except:
            return None,None
            
        

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
            if not text.isdigit():
                decoded = text.encode('latin').decode('unicode_escape')
        except:
            pass
        
        return decoded

class Hashing:
    @staticmethod
    def get_md5(text: str):
        return hashlib.md5(text.encode()).hexdigest()

class CastDB:
    def cast_column(column_name, data_type):
        if data_type not in ["character","text", "character varying"]:
            return f"{column_name}::varchar(255)"
        else:
            return column_name