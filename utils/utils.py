from colored import Style, fore, back
import hashlib
import re
from base64 import b64decode
import magic
import mimetypes

class Util:
    @staticmethod
    def is_base64(text)->tuple[bytes,str]:
        if text.startswith('data:'):
            fragments = text.split(';')
            if len(fragments)>1:
                return Util.try_convert_b64(fragments[1].split(',',1)[1])
        
        if len(text) % 4 != 0:
            return None,None
        
        # Check if all characters are valid
        if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', text):
            return None,None

        try:
            # Check if it has a checksum character
            if len(text) > 1 and text[-1] == '=' and text[-2] == '=':
                return Util.try_convert_b64(text)
            elif len(text) > 0 and text[-1] == '=':
                return Util.try_convert_b64(text)
            else:
                return Util.try_convert_b64(text)
        except:
            pass
            
        return None,None

    @staticmethod
    def try_convert_b64(text)->tuple[bytes,str]:
        b64bytes = b64decode(text)
        data_format = Util.get_data_type(text)
        return b64bytes,data_format
    
    @staticmethod
    def get_data_type(content)->str:
        decoded_bytes = b64decode(content[:100])
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(decoded_bytes)
        return mimetypes.guess_extension(file_type).replace('.','')


    @staticmethod
    def print(message, color='green'):
        print(f'{fore(color)}[Info] - {message} {Style.reset}')

    @staticmethod
    def print_error(message):
        print(f'{fore("white")}{back("red")}[Critical]{Style.reset} {fore("white")}{message}{Style.reset}')
    
    @staticmethod
    def print_important(message):
        print(f'{fore("blue")}[Important!]{Style.reset} {fore("white")}{message}{Style.reset}')

    @staticmethod
    def print_info(category, message):
        print(f"{fore('yellow')}[{category}]{Style.reset}{message}")
    
    @staticmethod
    def print_line(message, color='green'):
        print(f'{fore(color)}[Info] - {message} {Style.reset}', end='', flush=True)
        
        

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