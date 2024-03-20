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
    
    def highlight_text(text:str, match_word:str, color:str='red')->str:
        text = str(text)
        formatted = False
        hight_light = re.sub(match_word, f"[{color}]{match_word}[reset]", text, flags=re.IGNORECASE)
        return Color.format(hight_light), formatted

        