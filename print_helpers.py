from colorama import Fore, Back, Style, init

CLI_CHAR = f"{Style.RESET_ALL}{Style.BRIGHT}>{Style.DIM}"


def print_logo_with_info(
    logo: str,
    headers: list[tuple],
    padding_min=12,
    header_start=4,
    header_color=Fore.WHITE,
    logo_color=Fore.RED,
):
    # Make copy of headers so we dont overwite original with our empty headers etc
    headers = headers.copy()

    # Calculate the padding needed for the information section
    padding = max(padding_min, max(len(header[0]) for header in headers))

    # Add empty headers to the start of the list
    [headers.insert(0, ("",)) for _ in range(header_start)]

    # Add empty headers to the end of the list to make up for the logo
    [headers.append(("",)) for _ in range(len(logo.splitlines()) - len(headers))]

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


def pluralise(count):
    return "s" if count != 1 else ""


if __name__ == "__main__":
    init()
    print_respect_cli("balls")
