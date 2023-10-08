import random
from colorama import Fore, Back, Style
import argparse
from steamwebapi.api import ISteamUser, IPlayerService, ISteamUserStats
import a2s
import requests
import json


parser = argparse.ArgumentParser(
    prog="cyrillic",
    description="Poison text with cyrillic characters for schemes",
    epilog="Have fun scheming!",
)

parser.add_argument(
    "-t", "--text", type=str, help="poison the supplied string with cyrillics"
)
parser.add_argument(
    "-ht",
    "--highlight-text",
    type=str,
    help="highlight cyrillic characters inside text",
)
parser.add_argument(
    "-p",
    "--players",
    action="store_true",
    help="pull all the players from a Steam server and poision their names",
)
parser.add_argument(
    "-a",
    "--address",
    type=str,
    default="play.unlimitedrp.cc:27015",
    help="address of the Steam server for extracting player names, in format IP:port",
)

parser.add_argument(
    "-u",
    "--usernames",
    action="store_true",
    help="get random usernames from a pastebin link and poison them",
)
parser.add_argument(
    "--usernames-link",
    type=str,
    default="https://pastebin.com/raw/MQeZjhrp",
    help="link to get usernames from",
)
args = parser.parse_args()

# Extract server address and port from command line arguments
server_address, server_port = args.address.split(":")
server_port = int(server_port)
address = (server_address, server_port)

n = 10
char_map = {
    "A": "А",
    "B": "В",
    "C": "С",
    "c": "с",
    "E": "Е",
    "a": "а",
    "e": "е",
    "o": "о",
    "P": "Р",
    "p": "р",
    "y": "у",
    "X": "Х",
    "x": "х",
    "i": "і",
    "I": "І",
    "j": "ј",
}


def convert_name(name):
    new_name = ""
    for c in name:
        if c in char_map.keys():
            new_name = new_name + Fore.RED + char_map[c] + Style.RESET_ALL
        else:
            new_name = new_name + c

    new_name = "".join(new_name)
    return new_name


def poison_server(address):
    for p in a2s.players(address):
        name = p.name.strip()
        print(convert_name(name))


if __name__ == "__main__":
    print(
        Fore.LIGHTGREEN_EX
        + "Cyrillic Text Poisoner "
        + Fore.BLUE
        + "v0.1"
        + Style.RESET_ALL
    )
    print(
        Fore.LIGHTGREEN_EX
        + "Foreign characters will be highlighted in red.\n"
        + Style.RESET_ALL
    )

    if args.text:
        print(args.text)
        print(convert_name(args.text))

    if args.players:
        poison_server(address)

    if args.usernames:
        # Get the usernames from the pastebin link
        r = requests.get(args.usernames_link)
        for name in r.text.split("\n"):
            print(convert_name(name))
