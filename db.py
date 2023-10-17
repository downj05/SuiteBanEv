import json
from time import time as timestamp
from time_helpers import ts_to_str
from colorama import Fore, Back, Style
from ip import get_public_ip
from hwid2 import get_hwid
from steam_client_accounts import get_latest_user_steam64


DATABASE_FILE = "db.json"

def check_in_database(ip: str, hwid: list, steam64: str):
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
        database = {"data": []}
        with open(DATABASE_FILE, "w") as file:
            json.dump(database, file)


def add_to_database(ip, hwid, steam64, duration, time_added=None):
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
