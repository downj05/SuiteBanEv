from colorama import Fore, Back, Style, init
from html.parser import HTMLParser
import re

CLI_CHAR = f"{Style.RESET_ALL}{Style.BRIGHT}>{Style.DIM}"


def print_logo_with_info(
    logo: str,
    headers: list[tuple],
    padding_min=12,
    padding_offset=2,
    header_start=4,
    header_color=Fore.WHITE,
    logo_color=Fore.RED,
):
    # Make copy of headers so we dont overwite original with our empty headers etc
    headers = headers.copy()

    # Calculate the padding needed for the information section
    # Ignore headers with only 1 element as these arent in the standard header: info format
    # As this is the case, we dont want the side of header to contribute to the padding
    padding = max(padding_min, max(len(header[0])
                  for header in headers if len(header) > 1)) + padding_offset

    # Add empty headers to the start of the list
    [headers.insert(0, ("",)) for _ in range(header_start)]

    # Add empty headers to the end of the list to make up for the logo
    [headers.append(("",))
     for _ in range(len(logo.splitlines()) - len(headers))]

    for i, (line_logo, header_info) in enumerate(zip(logo.splitlines(), headers)):
        # If header is empty, this is likely a blank line inserted for header_start
        # In this case just print the part of the logo

        # Prefix logo line with its colour
        line_logo = logo_color + line_logo
        if header_info[0] == "":
            print(line_logo)
            continue
        header = header_info[0]
        padding_spaces = " " * (padding - len(header))

        if len(header_info) > 1:
            values = header_info[1:]
            print(
                f"{line_logo}  {header_color}{header}:{padding_spaces}{Style.RESET_ALL}{', '.join([str(value) for value in values])}"
            )
        else:
            print(f"{line_logo}  {header_color}{header}")


def print_respect_cli(text):
    print("\n" + text, end=f"\n{CLI_CHAR}")


def _header(text, background=Back.BLUE, foreground=Fore.BLACK):
    print(background + foreground + Style.NORMAL + text)


def h1(text):
    _header(text, Back.BLACK, Fore.CYAN)


def h2(text):
    _header(text, Back.LIGHTCYAN_EX, Fore.BLACK)


def s(text):
    return Style.BRIGHT + Fore.CYAN + text + Style.RESET_ALL


def s2(text):
    return Style.BRIGHT + Fore.MAGENTA + text + Style.RESET_ALL


def fore_fromhex(hexcode):
    """print in a hex defined color"""
    hexcode = hexcode.replace("#", "")
    red = int(hexcode[0:2], 16)
    green = int(hexcode[2:4], 16)
    blue = int(hexcode[4:6], 16)
    return f"\x1B[38;2;{red};{green};{blue}m"


def pluralise(count):
    return "s" if count != 1 else ""


class UnturnedHTMLParser(HTMLParser):
    COLOR_MAP = {
        'black': '#000000',
        'silver': '#C0C0C0',
        'gray': '#808080',
        'white': '#FFFFFF',
        'maroon': '#800000',
        'red': '#FF0000',
        'purple': '#800080',
        'fuchsia': '#FF00FF',
        'green': '#008000',
        'lime': '#00FF00',
        'olive': '#808000',
        'yellow': '#FFFF00',
        'navy': '#000080',
        'blue': '#0000FF',
        'teal': '#008080',
        'aqua': '#00FFFF'
    }

    def __init__(self):
        super().__init__()
        self.styled_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'b':
            self.styled_text += Style.BRIGHT
            return
        if tag.startswith('color'):
            if not re.match(r'#(\d|[A-z]){6}', tag.split('=')[-1]):
                try:
                    hex = self.COLOR_MAP[tag.split('=')[-1]]
                except KeyError:
                    self.styled_text += Fore.WHITE
                    return
            else:
                hex = tag.split('=')[-1]
            self.styled_text += fore_fromhex(hex)
            return

    def handle_endtag(self, tag):
        if tag == 'b':
            self.styled_text += Style.NORMAL
        if tag.startswith('color'):
            self.styled_text += Fore.WHITE

    def handle_data(self, data):
        self.styled_text += data


def parse_html_string(input_string):
    parser = UnturnedHTMLParser()
    parser.feed(input_string)
    return parser.styled_text


def visible_len(string: str) -> int:
    """Return the visible length of a string, ignoring color codes"""
    return len(re.sub(r"\x1B\[\d+m", "", string))


if __name__ == "__main__":
    init()
    print_respect_cli("balls")
