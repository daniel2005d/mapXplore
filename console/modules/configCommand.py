import cmd2
from cmd2 import CommandSet, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser
from utils.ansiprint import AnsiPrint
from config.settings import Settings
from console.modules.argumentsManager import ArgumentsManager
import os


@with_default_category('Config Category')
class ConfigCommandSet(CommandSet, ArgumentsManager):
    def __init__(self, args, section=None) -> None:
        super().__init__()
        if hasattr(cmd2.Cmd,'do_set'):
            delattr(cmd2.Cmd, 'do_set')
        self._section = section
        self._config = Settings.setting[section]
    
        

    def set_config(self, args):
        print(self._config)

    def do_unset(self, args:cmd2.Statement):
        self.do_set(args)

    def complete_set(self, text, line, idx,endx):
        completions = []
        for item in self._config.keys():
            if item.startswith(text):
                completions.append(item)
        return completions
    
    def do_set(self, args:cmd2.Statement):
        if args.command == 'unset':
            Settings.set_value(self._section, args.arg_list[0], None)
        elif args.command == 'set':
            section = args.arg_list[0]
            option = args.arg_list[1]
            if section in self._config:
                Settings.set_value(self._section, section, option)

    def do_show(self, arg:cmd2.Statement):
        AnsiPrint.printSetting(self._section)