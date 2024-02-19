import json
import os
from colorama import Fore, Back, Style

DATABASE_FILE = "db.json"
DATABASE_SCHEMA = {"data": [], "servers": {}}  # Schema for the database file

# Schema for each ban entry
BAN_ENTRY_SCHEMA = {
    "ip": "",
    "hwid": "",
    "steam64": "",
    "duration": 0,
    "time_added": 0,
    "server": "",
}


class JsonBase:
    """
    Cheeky JSON-ORM like object, instances require a 'name' variable in __init__ that is assigned to self.
    """
    _table_name = "none"
    _database_file = DATABASE_FILE

    def _build_table(func):
        """
        Construct the database + table if it hasnt been made already
        """
        def wrapper(self, *args, **kwargs):
            # See if database exists:
            if not os.path.exists(DATABASE_FILE):
                print(f'JSONBase: build_table.wrapper: Creating JSON database {self._database_file}')
                with open(self._database_file, 'w') as f:
                    f.write(json.dumps({}))

            # See if table exists
            with open(self._database_file, 'r') as f:
                database = json.loads(f.read())
                if database.get(self._table_name, None) is None:
                    print(f"JSONBase: build_table.wrapper: table {self._table_name} does not exist in {self._database_file}!")
                    database[self._table_name] = {}

            with open(self._database_file, 'w') as f:
                json.dump(database, f, indent=4)

            
            result = func(self, *args, **kwargs)
            return result
        return wrapper

    @_build_table
    def insert(self):
        # Insert / Add the object to the database
        print(f"JsonBase.insert: adding object of len {len(self.__dict__)} and name '{self.name}' to table {self._table_name}")
        with open(self._database_file, "r") as file:
            database = json.load(file)

        entry = self.__dict__
        database[self._table_name][self.name.lower()] = entry

        with open(self._database_file, "w") as file:
            json.dump(database, file, indent=4)

    @_build_table
    def delete(self):
        # Delete the object from the database
        print(f"JsonBase.delete: removing object of len {len(self.__dict__)} and name '{self.name}' to table {self._table_name}")
        with open(self._database_file, "r") as file:
            database = json.load(file)

        database[self._table_name].pop(self.name.lower())

        with open(self._database_file, "w") as file:
            json.dump(database, file, indent=4)

    @classmethod
    def _from_database(cls, entry: dict):
        # print(f"JsonBase._from_database: create instance from {entry}")
        return cls(**entry)
    

    @classmethod
    @_build_table
    def all(cls, default=None) -> list[object]:
        with open(cls._database_file, "r") as file:
            database = json.load(file)
        if len(database[cls._table_name]) == 0:
            return default
        if isinstance(database[cls._table_name], list):
            return [cls._from_database(entry) for entry in database[cls._table_name]]
        return [cls._from_database(entry) for entry in database[cls._table_name].values()]


# class Server_Old:
#     def __init__(self, name: str, ip: str, port: int):
#         print("json_provider.Server.__init__: Warning: This class is deprecated! Use Server2 instead!")
#         self.name = name
#         self.ip = ip
#         self.port = port

#     def add_to_database(self):
#         create_database_if_not_exists()
#         with open(DATABASE_FILE, "r") as file:
#             database = json.load(file)

#         entry = {
#             "name": self.name,
#             "ip": self.ip,
#             "port": self.port,
#         }
#         database["servers"][self.name.lower()] = entry

#         with open(DATABASE_FILE, "w") as file:
#             json.dump(database, file, indent=4)

#     def remove_from_database(self):
#         create_database_if_not_exists()
#         with open(DATABASE_FILE, "r") as file:
#             database = json.load(file)

#         database["servers"].pop(self.name.lower())

#         with open(DATABASE_FILE, "w") as file:
#             json.dump(database, file, indent=4)

#     @staticmethod
#     def from_name(name: str):
#         create_database_if_not_exists()
#         with open(DATABASE_FILE, "r") as file:
#             database = json.load(file)
#         s = Server._from_database(database["servers"].get(name.lower()))
#         if s is None:
#             raise ValueError("Server not found")
#         return s

#     @staticmethod
#     def _from_database(entry: dict):
#         if entry is None:
#             return None
#         return Server(entry["name"], entry["ip"], entry["port"])

#     @staticmethod
#     def get_all_servers() -> list:
#         create_database_if_not_exists()
#         with open(DATABASE_FILE, "r") as file:
#             database = json.load(file)
#         return [Server._from_database(entry) for entry in database["servers"].values()]

#     @staticmethod
#     def server(*args, parent=None):
#         """
#         Usage: server add/remove/list
#         server add <name> <address:port>
#         server remove <name>
#         server list
#         Compatible with any command that takes <address:port> as an argument"""

#         if len(args) == 0:
#             raise TypeError("Invalid argument")

#         try:
#             if args[0] == "add":
#                 name = args[1]
#                 address, port = args[2].split(":")
#                 Server(name, address, int(port)).add_to_database()
#             elif args[0] == "remove":
#                 name = args[1]
#                 Server.from_name(name).remove_from_database()
#             elif args[0] == "list":
#                 servers = Server.get_all_entries()
#                 if len(servers) == 0:
#                     print("No servers in database")
#                 else:
#                     for server in servers:
#                         print(str(server))
#             else:
#                 raise TypeError("Invalid argument")
#         except IndexError:
#             raise TypeError("Invalid argument")
#         except ValueError:
#             raise TypeError("Invalid argument")

#     @staticmethod
#     def _is_server(text: str) -> bool:
#         # returns True if the text is a server name and false if it is an address:port
#         try:
#             Server.from_name(text)
#             return True
#         except ValueError:
#             pass
#         try:
#             address, port = text.split(":")
#             return False
#         except ValueError:
#             pass
#         return None

#     @staticmethod
#     def server_handler(text: str, tuple: bool) -> str:
#         """
#         Returns the server address:port regardless of whether the input is a server name or address:port
#         If tuple is True, returns a tuple of (address: str, port: int) instead of a string.
#         :param text: server name or address:port
#         :param tuple: whether to return a tuple or a string
#         """
#         # returns the server address:port regardless of whether the input is a server name or address:port
#         # if tuple is True, returns a tuple instead of a string
#         is_server = Server._is_server(text)
#         if is_server is None:
#             raise ValueError("Invalid server")
#         if is_server:
#             server = Server.from_name(text)
#             if tuple:
#                 return server.ip, server.port
#             else:
#                 return f"{server.ip}:{server.port}"
#         else:
#             if tuple:
#                 address, port = text.split(":")
#                 return address, int(port)
#             else:
#                 return text

#     def __str__(self):
#         return f"{Style.BRIGHT}{Fore.CYAN}{self.name}{Fore.BLACK}: {Fore.LIGHTBLUE_EX}({self.ip}:{self.port}){Style.RESET_ALL}"



if __name__ == "__main__":
    # d1 = DatabaseServer('test', '1.2.3.4', 2553)
    # d1.add_to_database()

    # d2 = DatabaseServer('playground', 'playground.me', 1024)
    # d2.add_to_database()

    pass

    

