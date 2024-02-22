from colored import Style, fore, back
import hashlib
import re
from base64 import b64decode

class Util:
    @staticmethod
    def is_base64(text)->tuple[bytes,str]:
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
        data_format = Util.get_data_type(b64bytes)
        return b64bytes,data_format
    
    @staticmethod
    def get_data_type(byte_content)->str:
        
        magic_numbers = {
            b'\xFF\xD8\xFF': 'JPEG',
            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'PNG',
            b'\x47\x49\x46\x38\x39\x61': 'GIF87a',
            b'\x47\x49\x46\x38\x37\x61': 'GIF89a',
            b'\x42\x4D': 'BMP',
            b'\x50\x4B\x03\x04': 'ZIP',
            b'\x50\x4B\x05\x06': 'ZIP',
            b'\x50\x4B\x07\x08': 'ZIP',
            b'\x25\x50\x44\x46': 'PDF',
            # Agrega más magic numbers para otros tipos de archivos aquí
        }

        # Search for the magic number in the first bytes of the decoded data
        for magic_number, file_type in magic_numbers.items():
            if byte_content.startswith(magic_number):
                return file_type
        
        
        return None

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