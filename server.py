from json_provider import JsonBase
from db_provider import LocalRemoteDatabaseServiceBase, SelectedDatabaseServerService
from db_models import Server as ServerRemote
from colorama import Fore, Style
from command import Command2
from typing import Union
import argparse

class JsonServer(JsonBase):
    """
    Improved Server(name, ip port) JSON storage that uses
    JSONBase as a base class for database interaction. 
    """
    
    _table_name = "servers"
    def __init__(self, name:str, ip: str, port: int):
        self.name = name
        self.ip = ip
        self.port = port
      
    @staticmethod
    def from_name(name: str):
        # create_database_if_not_exists()
        # with open(DATABASE_FILE, "r") as file:
        #     database = json.load(file)
        # s = Server._from_database(database["servers"].get(name.lower()))
        # if s is None:
        #     raise ValueError("Server not found")
        # return s
        s = [s for s in JsonServer.all() if s.name == name]
        if len(s) == 0:
            raise ValueError("Server not found")
        return s[0]

    @staticmethod
    def _is_server(text: str) -> bool:
        # returns True if the text is a server name and false if it is an address:port
        try:
            JsonServer.from_name(text)
            return True
        except ValueError:
            pass
        try:
            address, port = text.split(":")
            return False
        except ValueError:
            pass
        return None

    def __repr__(self) -> str:
        return f"{self.name} | {self.ip}:{self.port}"
    
    def __str__(self):
        return f"{Style.BRIGHT}{Fore.CYAN}{self.name}{Fore.BLACK}: {Fore.LIGHTBLUE_EX}({self.ip}:{self.port}){Style.RESET_ALL}"


class SelectedServerHandler():
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

    def __new__(cls) -> "SelectedServerHandler":
        if cls._instance is False:
            cls._instance = super(SelectedServerHandler, cls).__new__(cls)
            cls._instance._selected_server = None
        return cls._instance

    @property
    def selected(self) -> Union[JsonServer,ServerRemote]:
        return self._selected_server

    @selected.setter
    def selected(self, server: Union[JsonServer,ServerRemote]):
        self._selected_server = server
    
    
    # 2 types of handle input, handle input that only works with saved servers, and handle input that can use any address provided
    # The one that works with saved servers will be used for commands like "check" and "new" as we need to associate bans with a server we have saved
    # The one that works with any address will be used for commands like "players" and "poison" as we don't need have a saved server to use them

    # Handle input that only works with saved servers
    def fetch_from_server_list(self, server_name: str = None) -> Union[JsonServer, ServerRemote]:
        """
        Grabs a server from the server list
        Assume that the server_name is a server name, if there is no input, return the selected server
        If there is no selected server, raise an error
        :param server_name: the server name
        :param return_address_only: whether to return the address only or a server object
        :return: the server
        """

        print("fetch_from_server_list")

        # Handle selected server
        if server_name is None:
            print("server_name is None")
            if self.selected is None:
                # No input provided, and no server selected
                raise ValueError("No server selected")
            print(f"returning selected server: {self.selected}")
            return self.selected
        
        # Handle resolving name to server
        
        else:
            print(f"server_name provided, '{server_name}'")
            # Handle remote database
            if SelectedDatabaseServerService.selected() is not None:
                print("database selected!")
                print("fetching from database...")
                serverListService = ServerListService()
                return serverListService.from_name(server_name)
            # Handle local JSON database
            print("fetching from json database...")
            return JsonServer.from_name(server_name)

    # Handle input for commands that can use server address or server names
    def handle_address(
        self, input_str: str
    ) -> tuple[str, int]:
        """
        Handle input for commands that can use server address or server names
        Has all the same functionality as fetch_from_server_list, but can
        also handle the address:port format
        :param input_str: the input string
        :return: tuple(address, port)
        """
        # Handle address:port
        print("handle_address")
        server = self.fetch_from_server_list(input_str)
        if server:
            return server.ip, server.port
        else:
            address, port = input_str.split(":")
            return address, int(port)


class ServerListService(LocalRemoteDatabaseServiceBase):
    force_local = False
    
    def add_server(self, name, address, port):
        if self.database_selected():
            # Remote database
            server = ServerRemote(name=name, ip=address, port=port)
            self.db.add_record(server)
            return
        else:
            # Json database
            JsonServer(name, address, port).add_to_database()


    def list_servers(self):
        if self.database_selected():
            # Remote database
            return self.db.execute_query(ServerRemote).all()
        # Json database
        return JsonServer.all()
    
    def remove_server(self, name):
        if self.database_selected():
            # Remote database
            server = self.db.from_name(ServerRemote, name)
            self.db.delete_record(server)
            return
        else:
            # Json database
            JsonServer.from_name(name).remove_from_database()

    def from_name(self, name):
        if self.database_selected():
            # Remote database
            return self.db.from_name(ServerRemote, name)
        else:
            # Json database
            return JsonServer.from_name(name)


class ServerCommand(Command2):
    name:str = "server"
    usage:str = "server add/remove/list\n\nserver add <name> <address:port>\nserver remove <name>\nserver list"
    help:str = "use an alias for a servers details, compatible with all commands that take an address:port"
    def execute(self, *args):
            """
            Usage: server add/remove/list
            server add <name> <address:port>
            server remove <name>
            server list
            Compatible with any command that takes <address:port> as an argument"""
            if len(args) == 0:
                raise TypeError("Invalid argument")

            serverList = ServerListService()

            try:
                if args[0] == "add":
                    name = args[1]
                    address, port = args[2].split(":")
                    serverList.add_server(name, address, int(port))
                elif args[0] == "remove":
                    name = args[1]
                    serverList.remove_server(name)
                elif args[0] == "list":
                    servers = serverList.list_servers()
                    if len(servers) == 0:
                        print("No servers in database")
                    else:
                        for server in servers:
                            print(str(server))
                else:
                    raise TypeError("Invalid argument")
            except IndexError:
                raise TypeError("Invalid argument")
            except ValueError:
                raise TypeError("Invalid argument")

# def select_cmd(*args, parent):
#     parser = argparse.ArgumentParser(
#         prog=parent.name, add_help=False, usage=parent.usage
#     )
#     parser.add_argument("server", nargs="?", type=str, default=None)
#     args = parser.parse_args(args)
#     select_handler = SelectedServerHandler()
#     if args.server is None:
#         if select_handler.get_selected_server() is not None:
#             print(
#                 f"{Fore.YELLOW}Unselected server {str(select_handler.get_selected_server())}"
#             )
#             select_handler.deselect_server()
#             return
#         else:
#             raise Exception("No server provided")
#             return

#     server = select_handler.handle_saved(args.server)
#     select_handler.set_selected_server(server)
#     print(f"{Fore.GREEN}Selected server {str(server)}")
#     return
# command=command.Command(
#             "select",
#             select_cmd,
#             help="select a server for use when recording/checking bans",
#             usage="provide a server name to select it\nselect <name>\nleave blank to unselect the current server",
#         )
class SelectServerCommand(Command2):
    name:str = "select"
    usage:str = "provide name to select server, leave blank to unselect\nselect <name>\t- select a server\nselect\t- unselect the current server"
    help:str = "select a server for use when recording/checking bans"
    def execute(self, *args):
        parser = argparse.ArgumentParser(
            prog=self.name, add_help=True, usage=self.name)
        
        parser.add_argument("server", nargs="?", type=str, default=None)
        args = parser.parse_args(args)
        select_handler = SelectedServerHandler()
        if args.server is None:
            if select_handler.selected is not None:
                print(
                    f"{Fore.YELLOW}Unselected server {str(select_handler.selected)}"
                )
                select_handler.selected = None
                return
            else:
                raise Exception("No server provided")
                return
        
        server = select_handler.fetch_from_server_list(args.server)
        select_handler.selected = server
        print(f"{Fore.GREEN}Selected server {str(server)}")
        return


if __name__ == '__main__':
    servers  = SelectedServerHandler()
    serverlist = ServerListService()
    serverlist.add_server("nylex", "play.nylex.me", 27015)
    print(servers.fetch_from_server_list("nylex"))
    print(servers.fetch_from_server_list("farttopia"))