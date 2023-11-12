from colorama import init, Fore, Back, Style
from db import Server
import traceback


class Command:
    """
    Command object to be used with the CommandHandler
    Stores the name, help, usage, and function of a command
    """

    def __init__(self, name: str, func, help: str = "", usage: str = "", allow_exit: bool = False):
        self.name = name
        self.usage = usage
        self.help = help
        self.func = func
        self.allow_exit = allow_exit

    def print_help(self, usage: bool = True):
        print(
            f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{self.name}{Fore.BLACK} - {self.help}"
        )
        # If usage is enabled, and there is a usage string, print it
        if self.usage not in ("", None) and usage:
            print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Usage: {self.usage}")

    def execute(self, *args):
        self.func(*args, parent=self)


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
            print(Fore.RED + Style.BRIGHT +
                  f"Error: {str(e)}" + "\n" + HELP_MSG)
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


class SelectedServerHandler:
    """
    Class for handling the selected server
    _instance is made False so that the __new__ method will run
    __new__ will only run once, so the instance will be saved
    __new__ sets the instance's selected_server to None
    """
    _instance = False

    def __init__(self):
        """
        This will only run once, when the instance is created
        """
        print("init")

    def __new__(cls) -> "SelectedServerHandler":
        if cls._instance is False:
            print("creating first instance!")
            cls._instance = super(SelectedServerHandler, cls).__new__(cls)
            print(f"{cls._instance} -> None")
            cls._instance.selected_server = None
        print("new object, selected server:",
              str(cls._instance.selected_server))
        return cls._instance

    # Set the selected server from a string
    def set_selected_server(self, server: str):
        """
        Set the selected server from a string/server instance
        """
        if isinstance(server, Server):
            print("setting selected server to", server)
            self.selected_server = server
        else:
            print("setting selected server to", server)
            self.selected_server = Server.from_name(server)

    # Deset the selected server
    def deselect_server(self):
        print("deselecting server")
        self.selected_server = None

    # Get the selected server
    def get_selected_server(self) -> Server:
        return self.selected_server

    # 2 types of handle input, handle input that only works with saved servers, and handle input that can use any address provided
    # The one that works with saved servers will be used for commands like "check" and "new" as we need to associate bans with a server we have saved
    # The one that works with any address will be used for commands like "players" and "poison" as we don't need have a saved server to use them

    # Handle input that only works with saved servers
    def handle_saved(self, input_str: str = None, tuple=False) -> Server:
        """
        Handle input for commands that only work with saved servers
        Assume that the input is a server name, if there is no input, return the selected server
        If there is no selected server, raise an error
        :param input_str: the input string
        :return: the server
        """
        if input_str is None or input_str == '':
            if self.selected_server is None:
                raise ValueError("No server selected")
            else:
                server = self.selected_server
        elif isinstance(input_str, str):
            server = Server.from_name(input_str)
        elif isinstance(input_str, list):
            server = Server.from_name(input_str[0])
        if tuple:
            return server.ip, server.port
        else:
            return server

    def handle_address(self, input_str: str | list[str] = None, tuple: bool = False) -> str | tuple:
        """
        Handle input for commands that can use server address or server names
        Also allow for no input, in which case return the selected server (run handle_saved)
        :param input_str: the input string
        :param tuple: whether to return a tuple or the address as a string
        :return: the server address
        """
        if input_str is None or input_str == '':
            return self.handle_saved(input_str=input_str, tuple=tuple)
        elif isinstance(input_str, str):
            return Server.server_handler(input_str, tuple=tuple)
        elif isinstance(input_str, list):
            return Server.server_handler(input_str[0], tuple=tuple)


if __name__ == "__main__":
    a = SelectedServerHandler()
    b = SelectedServerHandler()
    print(a is b)

    a.set_selected_server("panda")

    print(a.selected_server)
    print(b.selected_server)
    c = SelectedServerHandler()
    print(c.selected_server)
