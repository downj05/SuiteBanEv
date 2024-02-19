import json_provider
from time import time as timestamp
from time_helpers import ts_to_str, ts_to_str_ago, parse_duration, duration_to_str
from colorama import Fore, Back, Style

from hwid2 import get_hwid
from steam_client_accounts import get_latest_user_steam64
from ip import IpManager
import db_provider
import db_models
import time
from server import SelectedServerHandler
import argparse
import print_helpers as ph
import json


class BanDatabaseService(db_provider.LocalRemoteDatabaseServiceBase):
    """
    Service for managing bans in the database
    The database is an sql server of sorts.
    This service is superior to the JSON database service.
    """

    """
    The JSON Database is a local file that stores all the bans in a JSON format.
    It is a simple way to store bans without needing a full SQL server, and is easy to manage.
    """

    def add_ban(self, ip: str, hwid: list[str], steam64: int, duration: int, server: db_models.Ban, reason: str = None, time_added: int = None):
        """
        Add a ban to the database
        """
        if not self.database_selected():
            # Json/LOCAL alternative (not implemented)
            return
        if hwid is None:
            hwid = [None, None, None]
        hwid1, hwid2, hwid3 = hwid
        ban = db_models.Ban(ip=ip, hwid1=hwid1, hwid2=hwid2, hwid3=hwid3, steam64=steam64, duration=duration, server=server, reason=reason, time=time_added)
        self.db.add_record(ban)
    
    def all_bans(self) -> list[db_models.Ban]:
        """
        Get all bans from the database
        """
        if not self.database_selected():
            # Json/LOCAL alternative (not implemented)
            return
        
        return self.db.execute_query(db_models.Ban).all()

    def fetch_bans_for_match(self, ip: str, hwid: list[str], steam64: int, serverName: str = None) -> list[db_models.Ban]:
        """
        Check if a ban exists in the database
        """
        if not self.database_selected():
            # Json/LOCAL alternative (not implemented)
            return
        
        
        hwid1,hwid2,hwid3 = hwid
        # execute query, return all matching columns of steam64, hwid1, hwid2, hwid3 or ip
        bans = db_models.Ban.get_matching_bans(self.db.session, steam64, hwid1, hwid2, hwid3, ip, serverName)
        return bans
    

class AddBanCommand(Command2):

def check_ban_in_database(ip: str, hwid: list, steam64: str, server: str = None):
    create_database_if_not_exists()
    with open(json_provider.DATABASE_FILE, "r") as file:
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
        with open(json_provider.DATABASE_FILE, "r") as file:
            database = json.load(file)
    except FileNotFoundError:
        database = json_provider.DATABASE_SCHEMA
        with open(json_provider.DATABASE_FILE, "w") as file:
            json.dump(database, file)


def update_database():
    # will ensure that the database is up to date with the latest schema
    # without overwriting any existing data
    create_database_if_not_exists()
    with open(json_provider.DATABASE_FILE, "r") as file:
        database = json.load(file)
    for key in json_provider.DATABASE_SCHEMA.keys():
        if key not in database:
            database[key] = json_provider.DATABASE_SCHEMA[key]

    # ensure that all entries have the correct schema
    for entry in database["data"]:
        for key in json_provider.BAN_ENTRY_SCHEMA.keys():
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
                    entry[key] = json_provider.BAN_ENTRY_SCHEMA[key]

    with open(json_provider.DATABASE_FILE, "w") as file:
        json.dump(database, file, indent=4)


def add_ban_to_database(ip, hwid, steam64, duration, server, time_added=None):
    create_database_if_not_exists()
    if time_added is None:
        # Default to current time in Unix timestamp
        time_added = int(timestamp())

    with open(json_provider.DATABASE_FILE, "r") as file:
        database = json.load(file)

    entry = json_provider.BAN_ENTRY_SCHEMA.copy()
    entry["ip"] = ip
    entry["hwid"] = hwid
    entry["steam64"] = steam64
    entry["duration"] = duration
    entry["time_added"] = time_added
    entry["server"] = server

    database["data"].append(entry)

    with open(json_provider.DATABASE_FILE, "w") as file:
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
    with open(json_provider.DATABASE_FILE, "r") as file:
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
    server_handler = SelectedServerHandler()
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
    server_handler = SelectedServerHandler()

    ip = ip_manager.get_public_ip()
    hwid = get_hwid()
    steam64 = get_latest_user_steam64()

    if args.all:
        ban_results = check_ban_in_database(ip, hwid, steam64)
    else:
        server = server_handler.fetch_from_server_list(args.server)
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

    for field, status in ban_results.items():
        ph.h2(field)
        for i, entry in enumerate(status):
            if i == len(status) - 1:
                print("└─ " + entry)
            else:
                print("├─ " + entry)

class JsonBan(json_provider.JsonBase):
    _table_name = "data"
    def __init__(self, ip: str, hwid: list[str], steam64: int, duration: int, time_added: int, server: str):
        self.ip = ip
        self.hwid = hwid
        self.steam64 = steam64
        self.duration = duration
        self.time_added = time_added
        self.server = server
    
    @property
    def expired(self) -> bool:
        return (self.time_added + self.duration) < int(time.time())

    def from_identifier(ip: str, hwid: list[str], steam64: int) -> json_provider.JsonBase:
        for ban in JsonBan.all():
            if ban.ip == ip or ban.steam64 == steam64 or any(h in ban.hwid for h in hwid):
                return ban
        return None


    @staticmethod
    def identifier_banned(ip: str, hwid: list[str], steam64: int) -> bool:
        return JsonBan.from_identifier(ip, hwid, steam64) is not None

    def __repr__(self) -> str:
        return f"<JsonBan(ip={self.ip}, hwid={self.hwid}, steam64={self.steam64}, duration={self.duration}, time_added={self.time_added}, server={self.server})>"

if __name__ == '__main__':
    print(JsonBan.all())