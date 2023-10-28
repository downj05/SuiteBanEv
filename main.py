import json
from hwid2 import get_hwid, randomize_hwid
from steam_client_accounts import get_latest_user_steam64
from ip import get_public_ip
from time_helpers import git_time_str_to_time_ago, duration_to_str
import re
import time
import sys
from colorama import init, Fore, Back, Style
from datetime import datetime as dt
import human_readable as hr
import poison
import ctypes
import kill_bind
import random
from db import (
    update_database,
    add_ban_to_database,
    check_ban_in_database,
    ban_count_in_database,
    Server,
)
from update import (
    compare_versions,
    update_script,
    get_current_version_info,
    get_latest_version_info,
)
import print_helpers as ph
import command as cmd


init(autoreset=True)
current_version = get_current_version_info()
selected_server = None


def type_print(text, delay=0.1, color=Fore.WHITE, style=Style.NORMAL):
    for char in text:
        sys.stdout.write(f"{color}{style}{char}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(delay)


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


def new_ban(*args):
    global selected_server
    ip = get_public_ip()
    hwid = get_hwid()
    steam64 = get_latest_user_steam64()
    if len(args) > 0:
        server = Server.from_name(args[0])
        server_name = server.name
    else:
        assert isinstance(selected_server, Server), "No server selected or provided"
        server = selected_server
        server_name = selected_server.name
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


def check(*args):
    global selected_server

    ip = get_public_ip()
    hwid = get_hwid()
    steam64 = get_latest_user_steam64()

    if len(args) == 0:
        assert isinstance(selected_server, Server), "No server selected or provided"
        ban_results = check_ban_in_database(
            ip, hwid, steam64, server=selected_server.name
        )

    # if at least 1 arg and first arg is all, do all
    elif args[0] == "all":
        ban_results = check_ban_in_database(ip, hwid, steam64, server=None)

    # server name is argument
    elif args[0]:
        ban_results = check_ban_in_database(
            ip, hwid, steam64, server=Server.from_name(args[0]).name
        )

    for field, status in ban_results.items():
        ph.h1(field)
        for i, entry in enumerate(status):
            if i == len(status) - 1:
                print("└─ " + entry)
            else:
                print("├─ " + entry)


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


def poison_server(*args):
    if args[0] == "-s":
        address = Server.server_handler(args[1], tuple=True)
        poison.poison_server(address)
    else:
        [print(poison.convert_name(" ".join(args)))]


def bind_kill(key="f11"):
    try:
        kill_bind.toggle_bind(key)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Invalid bind {i[1]}: {str(e)}")


def select_cmd(*args):
    global selected_server
    if len(args) < 1:
        if selected_server is not None:
            print(f"{Fore.YELLOW}Unselected server {str(selected_server)}")
            selected_server = None
            return
        else:
            raise Exception("No server provided")
            return

    server_name = args[0]
    server = Server.from_name(server_name)
    selected_server = server
    print(f"{Fore.GREEN}Selected server {str(server)}")
    return


def version_string() -> str:
    if current_version is None:
        return f"{Fore.RED}{Style.DIM}Unknown"
    else:
        try:
            update_info = get_latest_version_info()

            # If outdated
            if compare_versions(update_info):
                return [
                    f"{Fore.YELLOW}{Style.DIM}{current_version[0][:7]}"
                    + f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX} - New update {git_time_str_to_time_ago(update_info[2])} [{update_info[0][:7]}]",
                    f"{Fore.LIGHTCYAN_EX}{update_info[1]}",
                ]

            # If up to date
            else:
                return f"{Fore.GREEN}{Style.DIM}{current_version[0][:7]}{Fore.LIGHTGREEN_EX}{Style.NORMAL} - Up to date!"
        except:
            return Fore.RED + "Failed to fetch latest version info"


if __name__ == "__main__":
    # update database
    update_database()

    # init commands
    handler = cmd.CommandHandler()
    handler.register(
        command=cmd.Command(
            "check",
            check,
            help="check if your ip/hwid/steam64 are in a logged ban on a server\nwill check the currently selected server if no argument is provided",
            usage="check <server>/all\n\nCheck on a specific server\ncheck <server>\n\nCheck against all servers\ncheck all",
        )
    )
    handler.register(command=cmd.Command("spoof", spoof, help="randomize your hwid"))
    handler.register(
        command=cmd.Command(
            "new",
            new_ban,
            help="record a new ban, length will be prompted upon running, server must be selected or provided",
            usage="new <server>",
        )
    )
    handler.register(
        command=cmd.Command(
            "poison",
            poison_server,
            help="poison given text with russian characters, can also retrieve poisoned playernames from an unturned server",
            usage="poison <text> or poison -s <address:port>",
        )
    )
    handler.register(
        command=cmd.Command(
            "bind",
            bind_kill,
            help="toggle a bind key to kill unturned, <key> is f11 by default",
            usage="bind <key>",
        )
    )

    handler.register(
        command=cmd.Command(
            "server",
            Server.server,
            help="use an alias for a servers details, compatible with all commands that take an address:port",
            usage="server add/remove/list\n\nserver add <name> <address:port>\nserver remove <name>\nserver list",
        )
    )

    handler.register(
        command=cmd.Command("update", update_script, help="update the program")
    )

    handler.register(
        command=cmd.Command(
            "select",
            select_cmd,
            help="select a server for use when recording/checking bans",
            usage="provide a server name to select it\nselect <name>\nleave blank to unselect the current server",
        )
    )

    handler.register(command=cmd.Command("quit", exit, help="exit the program"))

    with open(random.choice(("banner.txt", "banner2.txt")), "r", encoding="utf-8") as f:
        logo = Fore.RED + f.read()

    name = f"{Fore.RED}Smuggler{Fore.WHITE}Suite"
    name_len = 0
    for c in name:
        if c.isalpha():
            name_len += 1

    version_str = version_string()

    headers = [(name,), ("-" * name_len,), (f"Made By", f"{Fore.RED}W32")]

    if isinstance(version_str, list):
        headers.append(("Version", version_str[0]))
        headers.append(("New Changes", version_str[1]))
    else:
        headers.append(("Version", version_str))

    spoofing = f"{Fore.GREEN}{Style.BRIGHT}Enabled!"
    if not is_admin():
        spoofing = f"{Fore.RED}{Style.DIM}Disabled! - Please run as Administrator"
    headers.append(("HWID Spoofing", spoofing))
    headers.append((f"{len(handler._commands)} commands loaded",))
    server_count = len(Server.get_all_servers())
    ban_count = ban_count_in_database()

    headers.append(
        (
            (
                f"{server_count} server{ph.pluralise(server_count)} saved"
                + f" | {ban_count} ban{ph.pluralise(server_count)} recorded"
            ),
        )
    )
    ph.print_logo_with_info(logo, headers)

    while True:
        i = input(ph.CLI_CHAR)
        print(Style.RESET_ALL, end="")
        handler.handleInput(i)
