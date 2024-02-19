from colorama import Fore, Back, Style
import argparse
import a2s
import argparse
from server import SelectedServerHandler

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


def poison_server(address: tuple):
    for p in a2s.players(address):
        name = p.name.strip()
        print(convert_name(name))


def poison_command(*args, parent):
    # Ignore unknown args so an arbitrary amount of text can be passed
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)
    parser.add_argument("text", nargs="*", help="text to poison")
    parser.add_argument("-s", type=str, help="server address", default=None)
    args = parser.parse_args(args)
    server_handler = SelectedServerHandler()
    # Handle the server address as we do not need to use a saved server
    if args.s:
        address = server_handler.handle_address(args.s, tuple=True)
        poison_server(address)
    else:
        [print(convert_name(" ".join(args.text)))]
