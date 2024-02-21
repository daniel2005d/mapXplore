"""
Allow to find information over imported databases
"""
import argparse
from database.connection import Connection
from dbConnector import DbConnector
from searcher.console import SearchConsole
from searcher import console
import sys



# class Searcher(DbConnector):
#     def __init__(self, *argv) -> None:
#         super().__init__(*argv)
#         self._type = argv[0].type
#         self._value = argv[0].value
#         connection = self._createDBEngine()
#         self._console = SearchConsole()
#         self._console.set_config(connection=connection)

#     def search(self):
#         self._console.print_information()
#         sys.exit(self._console.cmdloop())

console.main()