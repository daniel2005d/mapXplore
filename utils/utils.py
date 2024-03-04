from colored import Style, fore, back
import hashlib
from base64 import b64decode
import magic
import mimetypes
import os
from utils.filemanager import FileManager

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
    
    def get_readable_content(content:bytes)->str:
        text = ""
        allowed_bytes = set(range(32, 127)) | {10,13}
        allowed_bytes |= set(range(192, 238))
        allowed_bytes |= set(range(240, 256)) # Add Latin chars
        for byte in content:
            if byte not in allowed_bytes:
                text+=" "
            else:
                text+=chr(byte)
        
        return text

    @staticmethod
    def is_base64(text)->tuple[bytes,str]:
        text_type = None
        content = None
        file_manager = FileManager()
        try:
            if text.isdigit():
                return None, None
            else:
                try:
                    content_bytes = b64decode(text)
                    text_type = magic.from_buffer(content_bytes, mime=True)
                    if text_type == 'text/plain':
                        text_type = 'txt'
                        if text[-2:] == '==':
                            content = Util.get_readable_content(content_bytes)
                        elif Util.is_readable(content_bytes):
                            content = content_bytes.decode('latin')
                        else:
                            return None,None
                    elif text_type == 'text/xml':
                        text_type = 'xml'
                        content = Util.get_readable_content(content_bytes)
                    elif text_type == 'application/pdf':
                        text_type = 'pdf'
                        content = file_manager.read_pdf(content_bytes)
                    elif text_type == 'application/octet-stream':
                        return None, None
                except UnicodeDecodeError as ue:
                    return content, text_type
                
                if content is None:
                    return file_manager.get_file_type(text)
                # elif not Util.is_readable(content):
                #     content = Util.get_readable_content(content_bytes)
                
                return content, text_type

        except Exception as e:
            return content, text_type
            
        

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