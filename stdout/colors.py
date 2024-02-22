from colored import Style, Fore, Back, fore, style
import re

class Color:
    
    @staticmethod
    def print_allcolors():
        for color in Style._COLORS:
            print(f"{fore(color)}{color}{Style.reset}")
    @staticmethod
    def format(message):
        pattern = r'\[([^]]+)\]'
        
        for color in re.findall(pattern, message):
            forecolor=''
            if color == 'reset':
                forecolor = Style.reset
            elif color == 'bold':
                forecolor = Style.BOLD
            elif color in Style._COLORS:
                forecolor = fore(color)
            

            if forecolor != '':
                message=message.replace(f"[{color}]", f"{forecolor}")
        
        return message

    @staticmethod
    def print_error(message):
        Color.print(f"[red][-] {message}[reset]")
    
    @staticmethod
    def print_info(message):
        Color.print(f"[blue][!] {message}[reset]")
    
    @staticmethod
    def print(message):
        print(Color.format(message))
    
    def format_string(text:str, match_word:str)->str:
        text = str(text)
        formatted = False
        matches = re.search(match_word, text, flags=re.IGNORECASE)
        hight_light = text
        if matches:
            formatted = True
            start = matches.start()
            end = matches.end()
            hight_light = Color.format(f"{text[:start]}[red]{text[start:end]}[reset]{text[end:]}")
        
        return hight_light, formatted

        