import json
from time import time as timestamp
from time_helpers import ts_to_str, ts_to_str_ago, parse_duration, duration_to_str
from colorama import Fore, Back, Style
from hwid2 import get_hwid
from steam_client_accounts import get_latest_user_steam64
from ip import IpManager
import time
import command
import argparse
import print_helpers as ph


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


def check_ban_in_database(ip: str, hwid: list, steam64: str, server: str = None):
    create_database_if_not_exists()
    with open(DATABASE_FILE, "r") as file:
        database = json.load(file)

    current_time = int(timestamp())
    results = {"ip": [], "hwid": [], "steam": []}

    for entry in database["data"]:
        # If server is none, check all servers
        if server is not None:
            if server not in entry.get("server", ""):
                continue
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
    no_ban_status(results["hwid"], " | ".join([i[:8] for i in hwid]))
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

    # ensure that all entries have the correct schema
    for entry in database["data"]:
        for key in BAN_ENTRY_SCHEMA.keys():
            if key not in entry:
                # prompt user to enter server name if it doesn't exist
                if key == "server":
                    prompt = (
                        f"{Fore.RED}Ban from {ts_to_str_ago(entry.get('time_added'))} is not tied to any server!"
                        + f"\n{Fore.YELLOW}{Style.NORMAL}You need to provide the NAME/ALIAS of the server that this ban is from. Example: 'unlimited', 'nylex', 'dt'"
                        f"\n{Fore.BLACK}{Style.BRIGHT}(Note: The server name you provide will need to be added to the server list with the 'server add' command for 'check' to work!)\n"
                    )
                    entry[key] = (
                        input(
                            prompt
                            + Fore.GREEN
                            + Style.BRIGHT
                            + "Server name: "
                            + Fore.LIGHTCYAN_EX
                        )
                        .strip()
                        .lower()
                    )
                else:
                    entry[key] = BAN_ENTRY_SCHEMA[key]

    with open(DATABASE_FILE, "w") as file:
        json.dump(database, file, indent=4)


def add_ban_to_database(ip, hwid, steam64, duration, server, time_added=None):
    create_database_if_not_exists()
    if time_added is None:
        # Default to current time in Unix timestamp
        time_added = int(timestamp())

    with open(DATABASE_FILE, "r") as file:
        database = json.load(file)

    entry = BAN_ENTRY_SCHEMA.copy()
    entry["ip"] = ip
    entry["hwid"] = hwid
    entry["steam64"] = steam64
    entry["duration"] = duration
    entry["time_added"] = time_added
    entry["server"] = server

    database["data"].append(entry)

    with open(DATABASE_FILE, "w") as file:
        json.dump(database, file, indent=4)


def get_ban_status(entry, current_time):
    time_added = ts_to_str(entry["time_added"])
    server = f" on {Fore.CYAN}{entry.get('server', 'unknown server')}{Style.RESET_ALL}"
    if entry["duration"] == -1:
        return Fore.RED + Style.BRIGHT + f"banned permanently at {time_added}" + server
    ban_expiry_time = entry["time_added"] + entry["duration"]
    if current_time < ban_expiry_time:
        return (
            Fore.LIGHTRED_EX
            + Style.BRIGHT
            + f"banned at {time_added} for {entry['duration']}"
            + server
        )
    else:
        return (
            Fore.YELLOW
            + Style.DIM
            + f"expired on {ts_to_str(ban_expiry_time)}"
            + server
        )


def ban_count_in_database(server: str = None) -> int:
    create_database_if_not_exists()
    with open(DATABASE_FILE, "r") as file:
        database = json.load(file)

    count = 0
    for entry in database["data"]:
        if server is not None:
            if server not in entry.get("server", ""):
                continue
        count += 1
    return count


def no_ban_status(r: list, val):
    if len(r) == 0:
        r.append(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"no bans! [{val}]")


ip_manager = IpManager()


def new_ban_cmd(*args, parent=None):
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage
    )

    parser.add_argument("server", nargs="?", type=str, default=None)

    parser.add_argument("-a", "--account", action="store_true", default=False)

    args = parser.parse_args(args)
    server_handler = command.SelectedServerHandler()
    server = server_handler.handle_saved(args.server)
    server_name = server.name

    if not args.account:
        ip = ip_manager.get_public_ip()
        hwid = get_hwid()
    else:
        print(f"{Fore.YELLOW}{Style.DIM}Account only ban! HWID and IP will be ignored!")
        ip = None
        hwid = None
    steam64 = get_latest_user_steam64()
    while True:
        i = input(
            f"{Fore.RED}Duration (e.g. 120s, 5m, 8h, 3d, 6w, 2M, 2y, perm): {Fore.YELLOW}"
        )
        try:
            duration = parse_duration(i)
            break
        except ValueError as e:
            print(f"Invalid duration: {str(e)}")

    time_added = int(time.time())
    add_ban_to_database(
        ip=ip,
        hwid=hwid,
        steam64=steam64,
        duration=duration,
        time_added=time_added,
        server=server_name,
    )
    print(
        f"{Fore.GREEN}{Style.BRIGHT}Added ban of length {Fore.MAGENTA}{duration_to_str(duration)}{Fore.GREEN} to database on the server {str(server)}"
    )


def check_cmd(*args, parent=None):
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage
    )

    parser.add_argument("server", nargs="?", type=str, default=None)
    parser.add_argument("-a", "--all", action="store_true", default=False)
    args = parser.parse_args(args)
    server_handler = command.SelectedServerHandler()

    ip = ip_manager.get_public_ip()
    hwid = get_hwid()
    steam64 = get_latest_user_steam64()

    if args.all:
        ban_results = check_ban_in_database(ip, hwid, steam64)
    else:
        server = server_handler.handle_saved(args.server)
        ban_results = check_ban_in_database(ip, hwid, steam64, server=server.name)

    max_status_len = 0
    for _, s in ban_results.items():
        for e in s:
            if ph.visible_len(e) > max_status_len:
                max_status_len = ph.visible_len(e)
    max_status_len += 3

    if args.all:
        s = "All servers"
    else:
        s = server.name.capitalize()
    ph.h1(s + (" " * (max_status_len - len(s))))
    print()

    for field, status in ban_results.items():
        ph.h2(field)
        for i, entry in enumerate(status):
            if i == len(status) - 1:
                print("└─ " + entry)
            else:
                print("├─ " + entry)


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
        database["servers"][self.name.lower()] = entry

        with open(DATABASE_FILE, "w") as file:
            json.dump(database, file, indent=4)

    def remove_from_database(self):
        create_database_if_not_exists()
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)

        database["servers"].pop(self.name.lower())

        with open(DATABASE_FILE, "w") as file:
            json.dump(database, file, indent=4)

    @staticmethod
    def from_name(name: str):
        create_database_if_not_exists()
        with open(DATABASE_FILE, "r") as file:
            database = json.load(file)
        s = Server._from_database(database["servers"].get(name.lower()))
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
    def server(*args, parent=None):
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
                        print(str(server))
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
        """
        Returns the server address:port regardless of whether the input is a server name or address:port
        If tuple is True, returns a tuple of (address: str, port: int) instead of a string.
        :param text: server name or address:port
        :param tuple: whether to return a tuple or a string
        """
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

    def __str__(self):
        return f"{Style.BRIGHT}{Fore.CYAN}{self.name}{Fore.BLACK}: {Fore.LIGHTBLUE_EX}({self.ip}:{self.port}){Style.RESET_ALL}"


if __name__ == "__main__":
    c = command.Command(
        "check",
        check_cmd,
        help="check if your ip/hwid/steam64 are in a logged ban on a server\nwill check the currently selected server if no argument is provided",
        usage="check <server>/<-a --all>\n\nCheck on a specific server\ncheck <server>\n\nCheck against all servers\ncheck -a\tcheck --all",
    )
    c.execute("nylex")
