import json
import argparse as argparse
from hwid import (
    get_drive_serial_number,
    set_drive_serial_number,
    increment_hwid,
    DRIVE_LETTER,
)
from steam_client_accounts import get_latest_user_steam64
from ip import get_public_ip
import re
import time
from colorama import init, Fore, Back, Style
from datetime import datetime as dt

DATABASE_FILE = "db.json"

init(autoreset=True)

parser = argparse.ArgumentParser(
    description="Track IP, HWID, and Steam64 ID status for a target Unturned server."
)
parser.add_argument(
    "-c",
    "--check",
    help="Check if the current IP, HWID, and Steam64 are in the database.",
    action="store_true",
)

parser.add_argument(
    "-n",
    "--new",
    help="Add a new ban with the current IP, HWID, and Steam64 to the database.",
    action="store_true",
)
parser.add_argument(
    "-d",
    "--duration",
    help='Specify the duration of the ban (e.g., "7d", "2w4d", or "perm").',
    default="perm",
)


parser.add_argument(
    "-t",
    "--time",
    help="Specify the time in Unix timestamp when adding a new ban.",
    default=None,
    type=int,
)


# Define the custom action function
def custom_action(arg_value):
    if arg_value is None:
        return 1
    try:
        return int(arg_value)
    except ValueError:
        parser.error("Invalid argument value. Please provide an integer.")


parser.add_argument(
    "-i",
    "--increment",
    help="Increment the HWID by 1",
    nargs="?",
    const=1,
    type=custom_action,
    default=False,
)
args = parser.parse_args()


class print_helpers:
    @staticmethod
    def _header(text, background=Back.BLUE, foreground=Fore.BLACK):
        print(background + foreground + Style.BRIGHT + text)

    @staticmethod
    def h1(text):
        print_helpers._header(text, Back.WHITE, Fore.BLACK)

    @staticmethod
    def h2(text):
        print_helpers._header(text, Back.LIGHTCYAN_EX, Fore.BLACK)

    @staticmethod
    def s(text):
        return Style.BRIGHT + Fore.CYAN + text + Style.RESET_ALL


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
        json.dump(database, file)


def ts_to_str(ts):
    if isinstance(ts, str):
        ts = int(ts)
    return dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


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


def check_in_database(ip, hwid, steam64):
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
        if entry["hwid"] == hwid:
            results["hwid"].append(
                (get_ban_status(entry, current_time)) + f" [{entry['hwid']}]"
            )
        if entry["steam64"] == steam64:
            results["steam"].append(
                (get_ban_status(entry, current_time)) + f" [{entry['steam64']}]"
            )

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

        return seconds


if __name__ == "__main__":
    if args.new:
        ip = get_public_ip()
        hwid = get_drive_serial_number()
        steam64 = get_latest_user_steam64()
        duration = parse_duration(args.duration)
        add_to_database(ip, hwid, steam64, duration, args.time)

    if args.check:
        ip = get_public_ip()
        hwid = get_drive_serial_number()
        steam64 = get_latest_user_steam64()

        ban_results = check_in_database(ip, hwid, steam64)

        print(Style.DIM + "checking status...")
        for field, status in ban_results.items():
            print_helpers.h2(field)
            if len(status) == 0:
                print(" - " + Fore.LIGHTGREEN_EX + "no bans!")
                continue
            for entry in status:
                print(" - " + entry)

    if args.increment:
        hwid = get_drive_serial_number()
        incremented_hwid = increment_hwid(hwid)
        print(
            f"HWID: {print_helpers.s(hwid)} will be changed to {print_helpers.s(incremented_hwid)} (drive is {DRIVE_LETTER}:)"
        )
        print("Confirm? (y/n) ", end="")
        confirm = input()
        if confirm.lower() == "y":
            r = set_drive_serial_number(incremented_hwid)
            if isinstance(r, bool):
                if r is True:
                    print(
                        Style.BRIGHT
                        + Fore.GREEN
                        + "Success! Please restart your computer to apply the changes."
                    )
                elif r is False:
                    print(
                        Style.BRIGHT
                        + Fore.RED
                        + "Failed! Please run this program as administrator."
                    )
            else:
                print(
                    Style.BRIGHT
                    + Fore.RED
                    + f"Failed! Error message: {print_helpers.s(r)}"
                )
        else:
            print("Cancelled.")
