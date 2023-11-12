import a2s
from db import Server
import print_helpers as ph
from colorama import Fore, Back, Style
from datetime import datetime as dt
import time_helpers as th


def player_pretty_print(player: a2s.Player):
    return (
        f"{Fore.WHITE}{player.name}" +
        f" [{Fore.LIGHTGREEN_EX}{th.format_time(int(player.duration))}{Fore.WHITE}]"
    )


def column_printer(matrix):
    # print out the matrix in columns

    # get max length cell
    max_cell = max(len(cell) for row in matrix for cell in row)
    # get max length row
    max_length = max(len(row) for row in matrix)

    for row in matrix:
        if len(row) < max_length:
            row.extend([""] * (max_length - len(row)))

    for row in matrix:
        for cell in row:
            print(cell.ljust(max_cell), end=" ")
        print()  # make a new line


def players(server: tuple):
    info = a2s.info(server)
    players = a2s.players(server)
    # Make header with relevant info
    top_header = ph.s(f"{info.server_name} {Style.RESET_ALL}{Fore.WHITE} ({info.player_count}/{info.max_players}) ") + \
        f"players [{Fore.LIGHTGREEN_EX}{int(info.ping*1000)}ms{Fore.WHITE}]\n"
    print(
        top_header + ph.parse_html_string(
            info.game) + ph.s(f" Map: {info.map_name}") + "\n" + f"{Fore.WHITE}{Style.DIM}{'━'*ph.visible_len(top_header)}" + Style.RESET_ALL
    )

    # Print the players in multiple columns
    # First we build a list of lists, each list is a row
    # Each row will have 3 columns, where each cell is a player
    # The list of lists will be passed to column_printer
    COLUMNS = 3
    rows = []
    for i in range(0, len(players), COLUMNS):
        row = []
        for player in players[i:i+COLUMNS]:
            row.append(player_pretty_print(player))
        rows.append(row)

    # Print columns
    if len(rows) == 0:
        print(f"{Fore.WHITE}{Style.DIM}No players online")
        return
    column_printer(rows)


if __name__ == '__main__':
    players("mexico")
