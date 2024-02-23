
class ArgumentsManager:
    def __init__(self) -> None:
        pass
    
    def _get_arguments(self, args, length=2):
        arguments = args.arg_list
        value,option = None, None
        for index, argv in enumerate(arguments):
            if index == 0:
                option = argv
            else:
                value = '' if value is None else value
                value+= " " + argv

        return option, value.lstrip() if value is not None else None
