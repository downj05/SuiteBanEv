import json
from hwid2 import get_hwid, randomize_hwid
from steam_client_accounts import get_latest_user_steam64
from ip import get_public_ip
from time_helpers import date_str_to_time_ago, ts_to_str
import re
import time
import sys
from colorama import init, Fore, Back, Style
from datetime import datetime as dt
import human_readable as hr
import poison
import ctypes
import kill_bind
from db import add_to_database, check_in_database
from update import (
    compare_versions,
    update_script,
    get_current_version_info,
    get_latest_version_info,
)
import print_helpers



init(autoreset=True)
current_version = get_current_version_info()

def type_print(text, delay=0.1, color=Fore.WHITE, style=Style.NORMAL):
    for char in text:
        sys.stdout.write(f"{color}{style}{char}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(delay)

def new_ban():
    ip = get_public_ip()
    hwid = get_hwid()
    steam64 = get_latest_user_steam64()
    while True:
        i = input("Duration (e.g. 1d, 1w, 1M, 1y, perm): ")
        try:
            duration = parse_duration(i)
            break
        except ValueError as e:
            print(f"Invalid duration: {str(e)}")

def parse_duration(duration_str):
    if duration_str.lower() == "perm":
        return -1
    else:
        # Use regular expressions to extract numeric values and units
        matches = re.findall(r"(\d+)([sdhwmMy])", duration_str)
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
    hwid = get_hwid()
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
    hwid = get_hwid()
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
        randomize_hwid()
    else:
        print("Cancelled.")


def ch(name, desc):
    print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{name}{Fore.BLACK} - {desc}")

def version_string() -> str:
    if current_version is None:
        return f"{Fore.RED}{Style.DIM}Unknown"
    else:
        try:
            update_info = get_latest_version_info()

            # If outdated
            if compare_versions(update_info):
                return f"{Fore.YELLOW}{Style.DIM}{current_version[0][:7]}" + \
                f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX} - New Update {date_str_to_time_ago(update_info[2])} {Fore.LIGHTCYAN_EX} '{update_info[1]}' [{update_info[0][:7]}]"

            # If up to date
            else:
                type_print(
                    current_version[0][:7],
                    delay=0.01,
                    color=Fore.GREEN,
                    style=Style.DIM,
                )
                print(Fore.LIGHTGREEN_EX + " - Up to date!" + Style.RESET_ALL)
                return f"{Fore.GREEN}{Style.DIM}{current_version[0][:7]}{Fore.LIGHTGREEN_EX}{Style.NORMAL} - Up to date!"
        except:
            return(Fore.RED + "Failed to fetch latest version info")


if __name__ == "__main__":
    with open("banner.txt", "r", encoding="utf-8") as f:
        logo = Fore.RED+f.read()
    
    name = f"{Fore.RED}Smuggler{Fore.WHITE}Suite"
    name_len = 0
    for c in name:
        if c.isalpha():
            name_len += 1

    headers = [
        (name,),
        ('-'*name_len,),
        (f"Made By", f"{Fore.RED}W32"),
        ("Version", version_string())
    ]

    spoofing = f"{Fore.GREEN}{Style.BRIGHT}Enabled!"
    if not is_admin():
        spoofing = f"{Fore.RED}{Style.DIM}Disabled! - Please run as Administrator"
    headers.append(("HWID Spoofing", spoofing))    

    print_helpers.print_logo_with_info(logo, headers)
    quit(0)
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
