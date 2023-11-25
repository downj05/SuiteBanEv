import requests
import os
import random
import command
import argparse
from colorama import Fore, Back, Style, init

# turdus-merula @ StackOverflow Aug 30, 2016 at 10:29

USERNAMES_FILE = 'usernames_666k.txt'

# Large list of 666K usernames (Approx 8MB in size)
USERNAMES_DRIVE_ID = '1W4YW1B8ua7ogKM5dFlmZNEjLR3si_ywq'
# Smaller list of usernames for testing (like 1kb)
USERNAMES_SMALL_DRIVE_ID = '1YDmZFSvDBDydER_18ki8ioqcQZ4Hgph5'


def create_usernames_if_not_exists():
    if not os.path.exists(USERNAMES_FILE):
        while True:
            print(
                f'{Fore.MAGENTA}Usernames file not found, download it? (y/n){Style.RESET_ALL}')
            print(
                f'{Style.BRIGHT}{Fore.BLACK}Note: The file takes up about 8MB of space{Style.RESET_ALL}')
            c = input(f'{Fore.MAGENTA}:{Fore.YELLOW}{Style.DIM}')
            if c.lower() not in ['y', 'yes']:
                if c.lower() in ['n', 'no']:
                    raise Exception('Username download cancelled by user')
                else:  # Invalid option provided
                    continue
            else:  # Yes
                break
        download_file_from_google_drive(
            USERNAMES_DRIVE_ID, USERNAMES_FILE)


def download_file_from_google_drive(id, destination):
    # When download is too big, google drive gives a warning that it can't scan the file for viruses
    # Under the hood you provide the value of the download_warning cookie to acknowledge this warning
    print(f'{Fore.BLACK}{Style.BRIGHT}Downloading file at [{id}]...')

    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        print(f"{Fore.BLACK}{Style.BRIGHT}Saving file to {destination}")
        with open(destination, "wb") as f:
            i = 0
            for chunk in response.iter_content(CHUNK_SIZE):
                i += 1
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
            print(
                f"{Fore.BLACK}{Style.BRIGHT}Wrote {i*CHUNK_SIZE//1000/1000}MB to {destination}")
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        print(f"{Fore.BLACK}{Style.BRIGHT}Bypassing Google Drive virus scan warning")
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


class UsernameGenerator():

    _instance = False
    _loaded = False

    def __init__(self):
        if UsernameGenerator._loaded:
            return
        create_usernames_if_not_exists()
        self._usernames = []
        with open(USERNAMES_FILE, 'r') as f:
            self._usernames.extend(f.read().splitlines())
        UsernameGenerator._loaded = True

    def __new__(cls) -> "UsernameGenerator":
        if cls._instance is False:
            cls._instance = super(UsernameGenerator, cls).__new__(cls)

        return cls._instance

    def random_username(self, count=1) -> list[str]:
        usernames = []
        for _ in range(count):
            usernames.append(random.choice(self._usernames))
        return usernames


def username_cmd(*args, parent=None):
    # Username command
    # Generates a random username, or multiple usernames optionally
    # Usage:
    # username <count (default 1)>
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)
    parser.add_argument('count', nargs='?', type=int, default=1)
    args = parser.parse_args(args)
    generator = UsernameGenerator()
    [print(f'{Fore.CYAN}{u}') for u in generator.random_username(args.count)]


if __name__ == "__main__":
    init(autoreset=True)
    generator = UsernameGenerator()
    generator2 = UsernameGenerator()
    generator3 = UsernameGenerator()
    print(generator.random_username(10))
    print(generator is generator2, generator2 is generator3)
