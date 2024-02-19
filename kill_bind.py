import keyboard
import argparse
import psutil
import print_helpers
from colorama import Fore, Style




def kill_unturned():
    print(
        f"{Fore.BLACK}{Style.BRIGHT}Killing any Unturned processes{Fore.RESET}"
    )
    for p in psutil.process_iter():
        if "unturned" in p.name().lower():
            try:
                print(
                    f"{Fore.BLACK}{Style.BRIGHT}Killing {Fore.MAGENTA}{Style.NORMAL}{p.name()}{Fore.RESET}"
                )
                p.kill()
            except Exception as e:
                print_helpers.print_respect_cli(
                    f"{Fore.RED}Failed to kill {p.name()}! {e}{Fore.RESET}"
                )


bind_enabled = False
bind_keys = []

def kill_cmd(*args, parent=None):
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)

    args = parser.parse_args(args)

    kill_unturned()


def toggle_bind(key: str):
    global bind_enabled
    global bind_keys

    bind_enabled = not bind_enabled
    if bind_enabled:
        print(
            f"{Fore.BLACK}{Style.BRIGHT}Kill bind {Fore.GREEN}{Style.BRIGHT}ON {Style.BRIGHT}{Fore.BLACK}[{Fore.MAGENTA}{Style.BRIGHT}{key}{Fore.RESET}{Fore.BLACK}{Style.BRIGHT}]{Fore.RESET}"
        )
        bind_keys.append(key)
        keyboard.add_hotkey(key, kill_unturned)

    else:
        for key in bind_keys:
            keyboard.remove_hotkey(key)
        bind_keys = []
        print(f"{Fore.BLACK}{Style.BRIGHT}Kill bind {Fore.RED}{Style.NORMAL}OFF")
