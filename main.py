import argparse
from hwid2 import get_hwid, randomize_hwid
from steam_client_accounts import get_latest_user_steam64
from ip import IpManager
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
from macros import swinger, wiggle
from players import players, player_monitor_cmd
from db import (
    update_database,
    add_ban_to_database,
    check_ban_in_database,
    ban_count_in_database,
    Server,
    check_cmd,
    new_ban_cmd
)
from update import (
    compare_versions,
    update_script,
    get_current_version_info,
    get_latest_version_info,
)

from usernames import username_cmd, UsernameGenerator

import print_helpers as ph
import command


init(autoreset=True)
current_version = get_current_version_info()
selected_server = None


ip_manager = IpManager()

parser = argparse.ArgumentParser(prog='Smuggler Suite')
parser.add_argument('--ignore-ssl', action='store_true', default=False,)
args = parser.parse_args()

if args.ignore_ssl:
    import urllib3
    # ignore ssl cert errors
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    urllib3.disable_warnings(urllib3.exceptions.SSLError)


def type_print(text, delay=0.1, color=Fore.WHITE, style=Style.NORMAL):
    for char in text:
        sys.stdout.write(f"{color}{style}{char}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(delay)


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        return False


def spoof(parent=None):
    c = input(
        Fore.LIGHTCYAN_EX
        + "Are you sure you want to spoof your hwid? (y/n):"
        + Style.RESET_ALL
    )
    if c.lower() == "y":
        randomize_hwid()
    else:
        print("Cancelled.")


def exit_program(parent=None):
    sys.exit(0)


def bind_kill(key="f11", parent=None):
    try:
        kill_bind.toggle_bind(key)
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Invalid bind {i[1]}: {str(e)}")


def select_cmd(*args, parent):
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)
    parser.add_argument('server', nargs='?', type=str, default=None)
    args = parser.parse_args(args)
    select_handler = command.SelectedServerHandler()
    if args.server is None:
        if select_handler.get_selected_server() is not None:
            print(
                f"{Fore.YELLOW}Unselected server {str(select_handler.get_selected_server())}"
            )
            select_handler.deselect_server()
            return
        else:
            raise Exception("No server provided")
            return

    server = select_handler.handle_saved(args.server)
    select_handler.set_selected_server(server)
    print(f"{Fore.GREEN}Selected server {str(server)}")
    return


def player_cmd(*args, parent):
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)

    parser.add_argument('server', nargs='?', type=str,
                        default=None)
    args = parser.parse_args(args)
    server_handler = command.SelectedServerHandler()
    server = server_handler.handle_address(args.server, tuple=True)
    players(server)


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
    handler = command.CommandHandler()
    handler.register(
        command=command.Command(
            "check",
            check_cmd,
            help="check if your ip/hwid/steam64 are in a logged ban on a server\nwill check the currently selected server if no argument is provided",
            usage="check <server>/<-a --all>\n\nCheck on a specific server\ncheck <server>\n\nCheck against all servers\ncheck -a\tcheck --all",
        )
    )
    handler.register(command=command.Command(
        "spoof", spoof, help="randomize your hwid"))
    handler.register(
        command=command.Command(
            "new",
            new_ban_cmd,
            help="record a new ban, length will be prompted upon running, server must be selected or provided",
            usage="new <server>",
        )
    )
    handler.register(
        command=command.Command(
            "poison",
            poison.poison_command,
            help="poison given text with russian characters, can also retrieve poisoned playernames from an unturned server",
            usage="poison <text> or poison -s <address:port>",
        )
    )
    handler.register(
        command=command.Command(
            "bind",
            bind_kill,
            help="toggle a bind key to kill unturned, <key> is f11 by default",
            usage="bind <key>",
        )
    )

    handler.register(
        command=command.Command(
            "server",
            Server.server,
            help="use an alias for a servers details, compatible with all commands that take an address:port",
            usage="server add/remove/list\n\nserver add <name> <address:port>\nserver remove <name>\nserver list",
        )
    )

    handler.register(
        command=command.Command("update", update_script,
                                help="update the program")
    )

    handler.register(
        command=command.Command(
            "select",
            select_cmd,
            help="select a server for use when recording/checking bans",
            usage="provide a server name to select it\nselect <name>\nleave blank to unselect the current server",
        )
    )

    handler.register(
        command=command.Command(
            "swinger",
            swinger,
            help="Automatically swing your weapon via left or right click",
            usage="swinger -d <delay> -a <action> -c <count>\nDefaults: delay=0.8, action=left (left, l, right, r), count=inf",
        )
    )

    handler.register(
        command=command.Command(
            "wiggle", wiggle, help="Automatically lean to break out of handcuffs/cable ties", usage="wiggle -d <delay> -kt <key time> -t <type>\nDefaults: delay=0.38, key time=0.05, type=inf (cuffs, handcuffs, cable, cabletie, inf, infinite)")
    )

    handler.register(
        command=command.Command(
            "players",
            player_cmd,
            help="Prints out a list of players on a server",
            usage="players <server>/<none (selected server)>",
        )
    )

    handler.register(
        command=command.Command(
            "monitor",
            player_monitor_cmd,
            help="Announce when players join/leave a server",
            usage="monitor <server>/<none (selected server)>",
        )
    )

    handler.register(
        command=command.Command("username", username_cmd,
                                help="Fetch random convincing usernames from a list of 666K Runescape usernames",
                                usage='username <count (default 1)>')
    )

    handler.register(command=command.Command(
        "quit", exit_program, help="exit the program", allow_exit=True))

    with open(random.choice(("banner.txt", "banner2.txt")), "r", encoding="utf-8") as f:
        logo = Fore.RED + f.read()

    name = f"{Fore.RED}Smuggler{Fore.WHITE}Suite"
    # Count number of characters in title for printing line break
    name_len = 0
    for c in name:
        # Only count letters, ignore ascii escape codes etc
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

    headers.append(
        ("",)
    )  # empty line to seperate help info

    headers.append(
        (f"{Fore.GREEN}Type {Fore.YELLOW}help <page 1-{len(handler._help_pages)}>{Fore.GREEN} for a list of commands",)
    )

    headers.append(
        (f"{Fore.GREEN}Or type {Fore.YELLOW}help <command>{Fore.GREEN} for help on a specific command",)
    )

    ph.print_logo_with_info(logo, headers)

    while True:
        i = input(ph.CLI_CHAR)
        print(Style.RESET_ALL, end="")
        handler.handleInput(i)
