from colorama import init, Fore, Back, Style
import traceback
from typing import Union


class Command:
    """
    Command object to be used with the CommandHandler
    Stores the name, help, usage, and function of a command
    """

    def __init__(
        self, name: str, func, help: str = "", usage: str = "", allow_exit: bool = False
    ):
        self.name = name
        self.usage = usage
        self.help = help
        self.func = func
        self.allow_exit = allow_exit
        print(f"command.Command: depcrecation warning for {name} - use Command2 instead")

    def print_help(self, usage: bool = True):
        print(
            f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{self.name}{Fore.BLACK} - {self.help}"
        )
        # If usage is enabled, and there is a usage string, print it
        if self.usage not in ("", None) and usage:
            print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Usage: {self.usage}")

    def execute(self, *args):
        self.func(*args, parent=self)

class Command2:
    """
    Command object to be used with the CommandHandler
    Stores the name, help, usage, and function of a command
    """
    name:str = None
    usage:str = ""
    help:str = ""
    allow_exit:bool = False

    def __init__(self):
        if not self.name:
            raise ValueError("Command2: name must be set")

    def print_help(self, usage: bool = True):
        print(
            f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{self.name}{Fore.BLACK} - {self.help}"
        )
        # If usage is enabled, and there is a usage string, print it
        if self.usage not in ("", None) and usage:
            print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Usage: {self.usage}")

    def execute(self, *args):
        print("Command2.execute: No command method has been assigned! This command doesn't do anyting!")

class CommandHandler:
    """
    Command handler to be used in a CLI application
    Can have commands be registered, and can show help for commands, etc
    """

    def __init__(self, traceback=False):
        self.traceback = traceback
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
            cmd.execute(*args)
            return True
        # except TypeError:
        #     print(Fore.RED + Style.BRIGHT +
        #           "invalid arguments" + "\n" + HELP_MSG)
        #     return False
        except SystemExit:
            # From argparse
            if cmd.allow_exit:
                raise SystemExit
            return False
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"Error: {str(e)}" + "\n" + HELP_MSG)
            if self.traceback:
                traceback.print_exc()
            return False

    def _help(self, arg: str = "help", parent=None):
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


if __name__ == "__main__":
    pass