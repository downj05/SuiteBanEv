from colorama import init, Fore, Back, Style


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


class CommandHandler:
    """
    Command handler to be used in a CLI application
    Can have commands be registered, and can show help for commands, etc
    """

    def __init__(self):
        self._commands = {}
        self.register(
            Command(
                "help",
                self._help,
                help="get info about a command",
                usage="help <command>",
            )
        )

    def register(self, command: Command):
        self._commands[command.name] = command

    def handleInput(self, usr_input: str):
        args = usr_input.strip().split(" ")
        command_name = args.pop(0)
        cmd = self._commands.get(command_name)
        if not cmd:
            print(Fore.RED + Style.BRIGHT + "invalid command")
            return False
        try:
            cmd.func(*args)
            return True
        except TypeError:
            print(Fore.RED + Style.BRIGHT + "invalid arguments")
            print(*args)
            return False
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"Error: {str(e)}")
            return False

    def _help(self, cmd_name: str = "help"):
        cmd = self._commands.get(cmd_name)
        if not cmd:
            print(Fore.RED + Style.BRIGHT + "command does not exist")
            return
        print(f"{cmd.name.capitalize()}: {cmd.help}")
        if cmd.usage not in ("", None):
            print(f"Usage: {cmd.usage}")
        return
