"""
Allow to find information over imported databases
"""
from database.connection import Connection

from console import console
import argparse
from utils.ansiprint import AnsiPrint
from middle import __VERSION__

def show_banner():
    banner = f"""[green]
 ____ ____ ____ ____ ____ ____ ____ ____ ____ 
||m |||a |||p |||X |||p |||l |||o |||r |||e ||
||__|||__|||__|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|
[reset]
    MapXplore - [bold]Version: {__VERSION__}[reset]
    Author: [bold]Daniel Vargas[reset]
    Repository: [bold]https://github.com/daniel2005d/mapXplore[reset]
"""



    
    AnsiPrint.print(banner)

parser = argparse.ArgumentParser()
parser.add_argument('--config', required=False)
args = parser.parse_args()

show_banner()
console.main(args)