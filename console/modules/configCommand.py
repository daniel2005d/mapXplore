import cmd2
from cmd2 import CommandSet, with_default_category
from utils.ansiprint import AnsiPrint
from config.settings import Settings
from console.modules.argumentsManager import ArgumentsManager

@with_default_category('Config Category')
class ConfigCommandSet(CommandSet, ArgumentsManager):
    def __init__(self, args) -> None:
        super().__init__()
        delattr(cmd2.Cmd, 'do_set')
        self.set_config(args)
        
    
    def set_config(self, args):
        Settings.setting["Database"]["host"]=args.host
        Settings.setting["Database"]["username"]=args.username
        Settings.setting["Database"]["password"]=args.password
        Settings.setting["Database"]["database"]=args.database
        Settings.setting["Database"]["dbtype"]=args.dbtype

    

    def complete_set(self, text, line, _, endidx):
        completions = [] 
        options = Settings.setting
        fragments = line.replace('set','').strip().split()
        section = None
        subsection = None
        if len(fragments) >= 1:
            section = fragments[0]
        
        if len(fragments) >= 2:
            subsection = fragments[1]
        
        if section:
            if section in Settings.setting:
                completions = tuple(Settings.setting[section].keys())
            else:
                for opt in Settings.setting:
                    if opt.startswith(section):
                        completions.append(opt)
        
        
            

        return completions if len(completions)>0 else tuple(Settings.setting.keys())
        
    def do_get(self, arg:cmd2.Statement):
        option, value = self._get_arguments(arg, 1)
        if option is not None:
            if option == 'hashes':
                for hash in Settings.allow_hashes:
                    AnsiPrint.print(f"[green]{hash}[reset]")

            elif value is None:
                for section in Settings.setting:
                    AnsiPrint.print(f"[green]{section}[reset]")
                    for option in Settings.setting[section]:
                        AnsiPrint.print(f"\t[bold]{option}[reset]: {Settings.setting[section][option]}")
            elif value not in Settings.setting:
                AnsiPrint.print_error("The configuration option does not exist")
            else:
                for section in Settings.setting[value]:
                    AnsiPrint.print(f"\t[bold]{section}:[reset]{Settings.setting[value][section]}")

    def do_set(self, args:cmd2.Statement):
        if len(args.arg_list) != 3:
            AnsiPrint.print_error("")
        else:
            # option, value = self.get_arguments(args)
            section = args.arg_list[0]
            option = args.arg_list[1]
            value = args.arg_list[2]

            if section in Settings.setting:
                if option in Settings.setting[section]:
                    Settings.setting[section][option]=value
                else:
                    AnsiPrint.print_error(f'Config option {option} {value} is not recognized')

            else:
                AnsiPrint.print_error(f'Argument {option} {value} is not recognized')
                return False
            