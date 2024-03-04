import cmd2
from cmd2 import CommandSet, with_default_category
from cmd2 import Cmd2ArgumentParser, with_argparser
from utils.ansiprint import AnsiPrint
from config.settings import Settings
from console.modules.argumentsManager import ArgumentsManager
import i18n.locale as locale
from middle.mapexception import MapXploreException


@with_default_category('Config Category')
class ConfigCommandSet(CommandSet, ArgumentsManager):
    def __init__(self, args, section=None) -> None:
        super().__init__()
        if hasattr(cmd2.Cmd,'do_set'):
            delattr(cmd2.Cmd, 'do_set')
        self._section = section
        if section is None:
            self._config = Settings.setting
        else:    
            self._section = section
            self._config = Settings.setting[section]
    
    def _ask_overwrite(self, filename, choose='N'):
        if choose.lower() != 'y':
            AnsiPrint.print(locale.get("config.overwrite_file"), end='')
            choose = input('')
            if choose == '':
                choose = 'y'
        
        if choose.lower() == 'y':
            Settings.save_settings(filename, override=True)
            AnsiPrint.print_locale("config.saved", filename=filename)

    parser = Cmd2ArgumentParser(add_help=locale.get("help.save_config"))
    parser.add_argument("filename", help=locale.get("help.filename"))

    @with_argparser(parser)
    def do_save(self, args):
        try:
            Settings.save_settings(args.filename, override=False)
        except MapXploreException as e:
            if not e.isError:
                self._ask_overwrite(args.filename, 'n')
            else:    
                AnsiPrint.print_error(e)
        except Exception as ex:
            AnsiPrint.print_error(ex)
        

    @with_argparser(parser)
    def do_load(self, args:cmd2.Statement):
        try:
            Settings.load_settings(args.filename)
            AnsiPrint.print_locale("config.loaded", filename=args.filename)
        except MapXploreException as e:
            AnsiPrint.print_error(e)
        


    def do_unset(self, args:cmd2.Statement):
        self.do_set(args)
    
    def complete_unset(self, text, line, idx, endx):
        return self.complete_set(text, line, idx, endx)

    def complete_set(self, text, line, idx, endx):
        completions = []
        for item in self._config.keys():
            if item.startswith(text):
                completions.append(item)
        return completions

    def do_set(self, args:cmd2.Statement):
        try:
            section, option, value = None, None, None
            if self._section is not None:
                section = self._section
                option = args.arg_list[0]
                value = args.arg_list[1] if args.command == 'set' else None
            else:
                section = args.arg_list[0]
                option  = args.arg_list[1]
                value = args.arg_list[2] if len(args.arg_list)>2 else None
            if args.command == 'unset':
                Settings.set_value(section, option, None)
            elif args.command == 'set':
                

                if section if self._section != section else option in self._config:
                    Settings.set_value(section, option, value)
                else:
                    AnsiPrint.print_error(locale.get("errors.section_config_error").format(section=section))
        except Exception as e:
            AnsiPrint.print_error(e)


    def do_show(self, arg:cmd2.Statement):
        if self._section is not None:
            AnsiPrint.printSetting(self._section)
        else:
            #subsection = self._config[arg.arg_list[0]] if len(arg.arg_list)>0 else self._config

            for section in self._config:
                AnsiPrint.print('')
                AnsiPrint.print_info(section)
                AnsiPrint.print('')
                AnsiPrint.printSetting(section)