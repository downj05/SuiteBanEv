from colorama import init, Fore, Back, Style
import traceback


class Command:
    """
    Command object to be used with the CommandHandler
    Stores the name, help, usage, and function of a command
    """

    def __init__(self, name: str, func, help: str = "", usage: str = ""):
        self.name = name
        self.usage = usage
        self.help = help
        self.func = func

    def print_help(self, usage: bool = True):
        print(
            f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{self.name}{Fore.BLACK} - {self.help}"
        )
        # If usage is enabled, and there is a usage string, print it
        if self.usage not in ("", None) and usage:
            print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Usage: {self.usage}")


class CommandHandler:
    """
    Command handler to be used in a CLI application
    Can have commands be registered, and can show help for commands, etc
    """

    def __init__(self):
        self._commands = {}
        self.PAGE_SIZE = 5  # page size for help pages
        self._help_pages = []
        self.register(
            Command(
                "help",
                self._help,
                help="get info about a command or view a page of commands",
                usage="help <command>/<page>",
            )
        )

    def register(self, command: Command):
        self._commands[command.name] = command
        # add to page, find a page that has room, or make a new one
        for page in self._help_pages:
            if len(page) < self.PAGE_SIZE:
                page.append(command)
                return
        self._help_pages.append([command])

    def handleInput(self, usr_input: str):
        args = usr_input.strip().split(" ")
        command_name = args.pop(0).lower()
        cmd = self._commands.get(command_name)
        if not cmd:
            print(Fore.RED + Style.BRIGHT + "invalid command")
            return False
        HELP_MSG = f"Do 'help {cmd.name}' for more info on this command"
        try:
            cmd.func(*args)
            return True
        # except TypeError:
        #     print(Fore.RED + Style.BRIGHT +
        #           "invalid arguments" + "\n" + HELP_MSG)
        #     return False
        except Exception as e:
            print(Fore.RED + Style.BRIGHT +
                  f"Error: {str(e)}" + "\n" + HELP_MSG)
            traceback.print_exc()
            return False

    def _help(self, arg: str = "help"):
        """
        Takes in 1 argument, either a command name or a page number
        If the argument is a command name, show the help for that command
        If the argument is a page number, show the help for that page
        If there is no argument, show the help for the help command
        """
        # See if the argument is a page number
        try:
            page = int(arg)
            # If the page number is out of range, show an error
            if page > len(self._help_pages) or page < 1:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + f"page does not exist, {len(self._help_pages)} pages available"
                )
                return
            # Print the page
            print(
                Style.BRIGHT
                + Fore.LIGHTYELLOW_EX
                + f"Page {page}/{len(self._help_pages)}"
            )
            for cmd in self._help_pages[page - 1]:
                cmd.print_help(usage=False)
            return
        except ValueError:
            pass
        cmd = self._commands.get(arg)

        # if the command doesn't exist, show an error
        if not cmd:
            print(Fore.RED + Style.BRIGHT + "command does not exist")
            return

        # if it does, show the help for that command
        cmd.print_help()


class ParsedArguments:
    """
    Parsed arguments object, used to store parsed arguments
    """

    def __init__(self):
        self._added_args = []
        pass


class ArgumentHandler:
    """
    Handler for arguments used in commands
    Lets you register arguments for a command, and parse arguments
    """
    STORE_TRUE = "store_true"
    STORE_FALSE = "store_false"
    STORE_VALUE = "store_value"
    VALUE_TYPES = ['str', 'int', 'float']

    def __init__(self, ignore_unknown_args=False):
        print('init arg handler')
        self._arguments = []
        self._parsed = ParsedArguments()
        self._ignore_unknown_args = ignore_unknown_args

    def register(self, name: str, value_type='str', default=None, action=STORE_VALUE):
        print(
            f'attempting to register arg {name} with value type {value_type} and default {default} and action {action}')
        if not name.startswith("-"):
            # positional argument
            arg_type = 'positional'
            # positional arguments cannot have a store action
            if action == self.STORE_TRUE or action == self.STORE_FALSE:
                raise ValueError(
                    f"cannot have a store action for positional argument '{name}'")
        else:
            # flag argument
            arg_type = 'flag'
            name = name[1:]

        if value_type not in self.VALUE_TYPES:
            raise ValueError(f"invalid type '{type}'")
        if action not in (self.STORE_TRUE, self.STORE_FALSE, self.STORE_VALUE):
            raise ValueError(f"invalid action '{action}'")

        if action == self.STORE_TRUE or action == self.STORE_FALSE:
            if default:
                raise ValueError(
                    f"cannot have a default value for action '{action}'")
            default = True if action == self.STORE_TRUE else False

        arg = {
            "name": name,
            "type": arg_type,
            "value_type": value_type,
            "default": default,
            "action": action,
        }

        self._arguments.append(arg)

        print(
            f'registered arg {name}:\n{self.get_arg_from_name(name)}')

    def get_arg_from_name(self, name: str):
        try:
            return self._arguments[self._arguments.index([arg for arg in self._arguments if arg['name'] == name][0])]
        except ValueError:
            return None
        except IndexError:
            return None

    def verify_arg_value(self, arg: dict, value: str):
        """
        Only used for non-store actions
        """
        if arg['value_type'] == 'int':
            try:
                return int(value)
            except ValueError:
                return False
        elif arg['value_type'] == 'float':
            try:
                return float(value)
            except ValueError:
                return False
        else:
            return value

    def handle_arg(self, arg_name: str, value: str = None):
        # verify the arg exists, if it does, store the value
        # if not a store action, verify the value provided by the user is valid
        print(f'handling arg {arg_name} with value {value}')
        arg = self.get_arg_from_name(arg_name)
        if not arg and not self._ignore_unknown_args:
            raise ValueError(f"argument does not exist: '{arg_name}'")
        elif not arg and self._ignore_unknown_args:
            print(f'ignoring unknown arg {arg_name}')
            return
        print(f"resolved '{arg_name}' to: {arg}")
        # Store actions use defaults for their logic
        if arg['action'] == self.STORE_TRUE or arg['action'] == self.STORE_FALSE:
            print('\tstore action')
            if value:
                raise ValueError(f"argument '{arg}' does not take a value")
            self.store_parsed(arg)
            return

        # If the value is None, and the action is not a store action, store the default value
        if not value:
            print('\tno value provided for non store action')
            self.store_parsed(arg)
            return

        # Verify the value is valid
        value = self.verify_arg_value(arg, value)
        if not value:
            raise ValueError(f"invalid value '{value}' for argument '{arg}'")

        # Store the parsed argument
        arg['value'] = value
        self.store_parsed(arg)

    def store_parsed(self, arg: dict):
        print(f'storing parsed arg {arg}')
        self._parsed.__dict__[arg['name']] = arg.get('value', arg['default'])
        print(
            f'stored parsed arg {arg} with value {arg.get("value", arg["default"])}')
        self._parsed._added_args.append(arg['name'])
        print(
            f'added arg {arg["name"]} to added args, total {len(self._parsed._added_args)}')

    def set_parsed_none(self):
        # set to none if not added so we can check if it was added
        for arg in self._arguments:
            print(f"checking if arg {arg} was added")
            if arg['name'] not in self._parsed._added_args:
                print(f"\targ {arg} was not added")
                self._parsed.__dict__[arg['name']] = None

    def parse(self, *args) -> ParsedArguments:
        # args will be a list of strings
        # arguments are passed like -a value

        for i, arg in enumerate(args):
            print("parsing arg", arg)
            if arg.startswith("-"):  # handle flag argument
                print("\tflag arg")
                arg = arg[1:]
                # check if the next argument is a value
                val = args[i + 1] if i + 1 < len(args) else None
                if val and not val.startswith("-"):
                    print("\t\tvalue provided with arg")
                    self.handle_arg(arg, val)
                else:
                    print("\t\tno value provided with arg")
                    self.handle_arg(arg)
            else:  # handle positional argument
                # if the previous argument was a flag, skip this argument
                if args[i - 1].startswith("-"):
                    continue

                self.handle_arg(arg)
        # set any args that weren't added to none so that accessing them doesn't throw an error
        self.set_parsed_none()

        return self._parsed


if __name__ == '__main__':
    def test_cmd(*args):
        parser = ArgumentHandler()
        parser.register('-a', value_type='int',
                        action=ArgumentHandler.STORE_VALUE)
        parser.register('-b', value_type='float',
                        action=ArgumentHandler.STORE_VALUE)
        parser.register('-c', action=ArgumentHandler.STORE_TRUE)

        args = parser.parse(*args)

        print(args.__dict__)
        if args.a:
            print(f"a: {args.a}")
        if args.b:
            print(f"b: {args.b}")
        if args.c:
            print(f"c: {args.c}")

    cmd_handler = CommandHandler()
    cmd_handler.register(Command('test', test_cmd,
                                 help='test command', usage='test <args>'))
    cmd_handler.handleInput('test -a 1 -b 2.5 ')
    cmd_handler.handleInput('test -a 1 -b 2.5')
    cmd_handler.handleInput('test -a 1')
    cmd_handler.handleInput('test -b 2.5')
    cmd_handler.handleInput('test -c')
    cmd_handler.handleInput('test')
