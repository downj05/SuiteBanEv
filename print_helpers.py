from colorama import Fore, Back, Style, init

CLI_CHAR = f"{Style.RESET_ALL}{Style.BRIGHT}>{Style.DIM}"


def print_respect_cli(text):
    print("\n" + text, end=f"\n{CLI_CHAR}")


def _header(text, background=Back.BLUE, foreground=Fore.BLACK):
    print(background + foreground + Style.NORMAL + text)


def h1(text):
    _header(text, Back.WHITE, Fore.BLACK)


def h2(text):
    _header(text, Back.LIGHTCYAN_EX, Fore.BLACK)


def s(text):
    return Style.BRIGHT + Fore.CYAN + text + Style.RESET_ALL


if __name__ == "__main__":
    init()
    print_respect_cli("balls")
