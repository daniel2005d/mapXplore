from colored import Style, fore, back
import hashlib


class Util:
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