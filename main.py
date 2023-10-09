import json
import hwid2
from steam_client_accounts import get_latest_user_steam64
from ip import get_public_ip
import re
import time
import sys
from colorama import init, Fore, Back, Style
from datetime import datetime as dt
import human_readable as hr
import poison
import ctypes
import kill_bind
from update import (
    compare_versions,
    update_script,
    get_current_version_info,
    get_latest_version_info,
)
import print_helpers

DATABASE_FILE = "db.json"

init(autoreset=True)


def type_print(text, delay=0.1, color=Fore.WHITE, style=Style.NORMAL):
    for char in text:
        sys.stdout.write(f"{color}{style}{char}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(delay)


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
        time_added = int(time.time())  # Default to current time in Unix timestamp

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


def ts_to_str(ts):
    if isinstance(ts, str):
        ts = int(ts)
    return dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def date_str_to_time_ago(date_str):
    # Takes in a date like '2023-10-09T11:12:32Z' and uses human_readable to convert it to a time ago string
    return hr.date_time(dt.now() - dt.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ"))


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


def check_in_database(ip: str, hwid: list, steam64: str):
    create_database_if_not_exists()
    with open(DATABASE_FILE, "r") as file:
        database = json.load(file)

    current_time = int(time.time())
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


def parse_duration(duration_str):
    if duration_str.lower() == "perm":
        return -1
    else:
        # Use regular expressions to extract numeric values and units
        matches = re.findall(r"(\d+)([dhwmMy])", duration_str)
        seconds = 0

        for match in matches:
            value, unit = match
            value = int(value)
            if unit == "s":
                seconds += value
            elif unit == "m":
                seconds += value * 60
            elif unit == "h":
                seconds += value * 3600
            elif unit == "d":
                seconds += value * 86400
            elif unit == "w":
                seconds += value * 604800
            elif unit == "M":
                seconds += value * 2592000  # Assuming 30 days in a month
            elif unit == "y":
                seconds += value * 31536000  # Assuming 365 days in a year
            else:
                raise ValueError(f"Invalid unit: {unit}")

        return seconds


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        return False


def new_ban():
    ip = get_public_ip()
    hwid = hwid2.get_hwid()
    steam64 = get_latest_user_steam64()
    while True:
        i = input("Duration (e.g. 1d, 1w, 1M, 1y, perm): ")
        try:
            duration = parse_duration(i)
            break
        except ValueError as e:
            print(f"Invalid duration: {str(e)}")

    time_added = int(time.time())
    add_to_database(ip, hwid, steam64, duration, time_added)


def check():
    ip = get_public_ip()
    hwid = hwid2.get_hwid()
    steam64 = get_latest_user_steam64()

    ban_results = check_in_database(ip, hwid, steam64)

    print(Style.DIM + "checking status...")
    for field, status in ban_results.items():
        print_helpers.h2(field)
        for entry in status:
            print(" - " + entry)


def spoof():
    c = input(
        Fore.LIGHTCYAN_EX
        + "Are you sure you want to spoof your hwid? (y/n):"
        + Style.RESET_ALL
    )
    if c.lower() == "y":
        if hwid2.random_set_convenient_save_data():
            print(
                Fore.LIGHTGREEN_EX
                + f"Successfully spoofed convenient save data! {Fore.MAGENTA}[{hwid2.get_convenient_save_data()}]"
                + Style.RESET_ALL
            )
        else:
            print(Fore.RED + "Failed to spoof convenient save data!" + Style.RESET_ALL)
        if hwid2.random_set_player_prefs():
            print(
                Fore.LIGHTGREEN_EX
                + f"Successfully spoofed player prefs! {Fore.MAGENTA}[{hwid2.get_player_prefs()}]"
                + Style.RESET_ALL
            )
        else:
            print(Fore.RED + "Failed to spoof player prefs!" + Style.RESET_ALL)
        if hwid2.random_set_windows_guid():
            print(
                Fore.LIGHTGREEN_EX
                + f"Successfully spoofed windows guid! {Fore.MAGENTA}[{hwid2.get_windows_guid()}]"
                + Style.RESET_ALL
            )
        else:
            print(Fore.RED + "Failed to spoof windows guid!" + Style.RESET_ALL)
    else:
        print("Cancelled.")


def ch(name, desc):
    print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{name}{Fore.BLACK} - {desc}")


if __name__ == "__main__":
    with open("banner.txt", "r", encoding="utf-8") as f:
        s = f.read()
    for line in s.splitlines():
        print(Fore.RED + line)
        time.sleep(0.05)
    type_print("Made by: ", delay=0.01, color=Fore.BLACK, style=Style.BRIGHT)
    type_print("W32", delay=0.01, color=Fore.CYAN, style=Style.BRIGHT)
    type_print("\tVersion: ", delay=0.01, color=Fore.BLACK, style=Style.BRIGHT)
    # type_print("2.0\n", delay=0.01, color=Fore.RED, style=Style.DIM)
    current_version = get_current_version_info()
    if current_version is None:
        type_print("Unknown", delay=0.01, color=Fore.RED, style=Style.DIM)
    else:
        try:
            update_info = get_latest_version_info()

            # If outdated
            if compare_versions(update_info):
                type_print(
                    current_version[0][:7],
                    delay=0.01,
                    color=Fore.YELLOW,
                    style=Style.DIM,
                )
                print(
                    Fore.LIGHTGREEN_EX
                    + f" - New Update {date_str_to_time_ago(update_info[2])} "
                    + Fore.LIGHTCYAN_EX
                    + f"'{update_info[1]}'  [{update_info[0][:7]}]"
                    + Style.RESET_ALL
                )

            # If up to date
            else:
                type_print(
                    current_version[0][:7],
                    delay=0.01,
                    color=Fore.GREEN,
                    style=Style.DIM,
                )
                print(Fore.LIGHTGREEN_EX + " - Up to date!" + Style.RESET_ALL)
        except:
            print(Fore.RED + "Failed to fetch latest version info")

    if not is_admin():
        print(
            Fore.RED
            + "Warning: You are not running this program as administrator. You will not be able to spoof HWID."
            + Style.RESET_ALL
        )

    type_print("Options:\n", delay=0.01, color=Fore.BLACK, style=Style.BRIGHT)
    ch("check", "check if you are banned")
    ch("spoof", "randomize your hwid")
    ch("new", "record a new ban")
    ch("poison <text>", "poison text with russian characters with ")
    ch(
        "poison -s <address:port>",
        "return all the poisoned playernames on an unturned server",
    )
    ch("bind <key>", "toggle a bind key to kill unturned, <key> is f11 by default")
    ch("update", "update the program")
    ch("quit", "exit the program")

    while True:
        i = input(print_helpers.CLI_CHAR).strip().split(" ")
        c = i[0].lower()
        try:
            if c == "check":
                check()
            elif c == "spoof":
                spoof()
            elif c == "new":
                new_ban()
            elif c == "poison":
                if i[1] == "-s":
                    address, port = i[2].split(":")
                    poison.poison_server((address, int(port)))
                else:
                    [print(poison.convert_name(i)) for i in i[1:]]
            elif c == "bind":
                if len(i) < 2:
                    kill_bind.toggle_bind("f11")
                else:
                    try:
                        kill_bind.toggle_bind(i[1])
                    except Exception as e:
                        print(
                            Fore.RED + Style.BRIGHT + f"Invalid bind {i[1]}: {str(e)}"
                        )

            elif c == "update":
                update_script()

            elif c == "quit":
                break
            else:
                print(Fore.BLACK + Style.BRIGHT + "Invalid command")
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"Error: {str(e)}")
