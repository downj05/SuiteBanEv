import json
from time import time as timestamp
from time_helpers import ts_to_str
from colorama import Fore, Back, Style
from ip import get_public_ip
from hwid2 import get_hwid
from steam_client_accounts import get_latest_user_steam64


DATABASE_FILE = "db.json"
DATABASE_SCHEMA = {"data": [], "servers": {}}  # Schema for the database file


def check_ban_in_database(ip: str, hwid: list, steam64: str):
    create_database_if_not_exists()
    with open(DATABASE_FILE, "r") as file:
        database = json.load(file)

    current_time = int(timestamp())
    results = {"ip": [], "hwid": [], "steam": []}

    for entry in database["data"]:
        if entry["ip"] == ip:
            results["ip"].append(
                (get_ban_status(entry, current_time) + f" [{entry['ip']}]")
            )
        if isinstance(entry["hwid"], list):
            for ban_hwid in hwid:
                if ban_hwid in entry["hwid"]:
                    results["hwid"].append(
                        (get_ban_status(entry, current_time)) + f" [{ban_hwid}]"
                    )
        if entry["steam64"] == steam64:
            results["steam"].append(
                (get_ban_status(entry, current_time)) + f" [{entry['steam64']}]"
            )

    # automatically add no bans msg if there are no bans
    no_ban_status(results["ip"], ip)
    no_ban_status(results["hwid"], hwid)
    no_ban_status(results["steam"], steam64)

    return results


def create_database_if_not_exists():
    try:
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)
    except FileNotFoundError:
        database = DATABASE_SCHEMA
        with open(DATABASE_FILE, "w") as file:
            json.dump(database, file)


def update_database():
    # will ensure that the database is up to date with the latest schema
    # without overwriting any existing data
    create_database_if_not_exists()
    with open(DATABASE_FILE, "r") as file:
        database = json.load(file)
    for key in DATABASE_SCHEMA.keys():
        if key not in database:
            database[key] = DATABASE_SCHEMA[key]
    with open(DATABASE_FILE, "w") as file:
        json.dump(database, file, indent=4)


def add_ban_to_database(ip, hwid, steam64, duration, time_added=None):
    create_database_if_not_exists()
    if time_added is None:
        time_added = int(timestamp())  # Default to current time in Unix timestamp

    with open(DATABASE_FILE, "r") as file:
        database = json.load(file)

    entry = {
        "ip": ip,
        "hwid": hwid,
        "steam64": steam64,
        "duration": duration,
        "time_added": time_added,
    }
    database["data"].append(entry)

    with open(DATABASE_FILE, "w") as file:
        json.dump(database, file, indent=4)


def get_ban_status(entry, current_time):
    time_added = ts_to_str(entry["time_added"])
    if entry["duration"] == -1:
        return Fore.RED + Style.BRIGHT + f"banned permanently at {time_added}"
    ban_expiry_time = entry["time_added"] + entry["duration"]
    if current_time < ban_expiry_time:
        return (
            Fore.LIGHTRED_EX
            + Style.BRIGHT
            + f"banned at {time_added} for {entry['duration']}"
        )
    else:
        return Fore.YELLOW + Style.DIM + f"expired on {ts_to_str(ban_expiry_time)}"


def no_ban_status(r: list, val):
    if len(r) == 0:
        r.append(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"no bans! [{val}]")


class Server:
    def __init__(self, name: str, ip: str, port: int):
        self.name = name
        self.ip = ip
        self.port = port

    def add_to_database(self):
        create_database_if_not_exists()
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)

        entry = {
            "name": self.name,
            "ip": self.ip,
            "port": self.port,
        }
        database["servers"][self.name] = entry

        with open(DATABASE_FILE, "w") as file:
            json.dump(database, file, indent=4)

    def remove_from_database(self):
        create_database_if_not_exists()
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)

        database["servers"].pop(self.name)

        with open(DATABASE_FILE, "w") as file:
            json.dump(database, file, indent=4)

    @staticmethod
    def from_name(name: str):
        create_database_if_not_exists()
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)
        s = Server._from_database(database["servers"].get(name))
        if s is None:
            raise ValueError("Server not found")
        return s

    @staticmethod
    def _from_database(entry: dict):
        if entry is None:
            return None
        return Server(entry["name"], entry["ip"], entry["port"])

    @staticmethod
    def get_all_servers() -> list:
        create_database_if_not_exists()
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)
        return [Server._from_database(entry) for entry in database["servers"].values()]

    @staticmethod
    def server(*args):
        """
        Usage: server add/remove/list
        server add <name> <address:port>
        server remove <name>
        server list
        Compatible with any command that takes <address:port> as an argument"""

        if len(args) == 0:
            raise TypeError("Invalid argument")

        try:
            if args[0] == "add":
                name = args[1]
                address, port = args[2].split(":")
                Server(name, address, int(port)).add_to_database()
            elif args[0] == "remove":
                name = args[1]
                Server.from_name(name).remove_from_database()
            elif args[0] == "list":
                servers = Server.get_all_servers()
                if len(servers) == 0:
                    print("No servers in database")
                else:
                    for server in servers:
                        print(
                            f"{Style.BRIGHT}{Fore.CYAN}{server.name}{Fore.BLACK}: {Fore.LIGHTBLUE_EX}{server.ip}:{server.port}"
                        )
            else:
                raise TypeError("Invalid argument")
        except IndexError:
            raise TypeError("Invalid argument")
        except ValueError:
            raise TypeError("Invalid argument")

    @staticmethod
    def _is_server(text: str) -> bool:
        # returns True if the text is a server name and false if it is an address:port
        try:
            Server.from_name(text)
            return True
        except ValueError:
            pass
        try:
            address, port = text.split(":")
            return False
        except ValueError:
            pass
        return None

    @staticmethod
    def server_handler(text: str, tuple: bool) -> str:
        # returns the server address:port regardless of whether the input is a server name or address:port
        # if tuple is True, returns a tuple instead of a string
        is_server = Server._is_server(text)
        if is_server is None:
            raise ValueError("Invalid server")
        if is_server:
            server = Server.from_name(text)
            if tuple:
                return server.ip, server.port
            else:
                return f"{server.ip}:{server.port}"
        else:
            if tuple:
                address, port = text.split(":")
                return address, int(port)
            else:
                return text
