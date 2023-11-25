import a2s
import argparse
import time
import command
import threading
import print_helpers as ph
from colorama import Fore, Back, Style
from datetime import datetime as dt
import time_helpers as th
from toasts import player_joined, player_left

player_monitor_thread_running = False


def player_pretty_print(player: a2s.Player):
    return (
        f"{Fore.WHITE}{player.name}" +
        f" [{Fore.LIGHTGREEN_EX}{th.format_time(int(player.duration))}{Fore.WHITE}]"
    )


def get_player_names(server, retries=3):
    for i in range(retries):
        try:
            players = a2s.players(server)
            break
        except:
            ph.print_respect_cli("Failed to get players, retrying... []")
            time.sleep(3)
    else:
        raise RuntimeError("Failed to get players")
    return [p.name for p in players]


def player_monitor_thread(polling_interval=10):
    global player_monitor_thread_running
    previous_players = get_player_names(
        player_monitor_thread_running['server'])

    ph.print_respect_cli(
        f"{Fore.CYAN}Player monitor started for {player_monitor_thread_running['name']}\n{Fore.WHITE}{Style.DIM}Run 'monitor' again to stop or 'monitor <server>' to monitor a different server")
    tick = 0
    tps = 20
    # Increment tick every 1/tps seconds, when tick reaches polling interval*tps, check for new/left players etc, reset tick
    while player_monitor_thread_running is not False and player_monitor_thread_running['running'] == True:
        tick += 1
        if tick >= polling_interval * tps:
            tick = 0
            players = get_player_names(player_monitor_thread_running["server"])

            # get new players
            new_players = [p for p in players if p not in previous_players]

            # get players that left
            left_players = [p for p in previous_players if p not in players]

            # print new players
            if new_players:
                for player in new_players:
                    ph.print_respect_cli(
                        f"{player} {Fore.LIGHTGREEN_EX}joined")
                    player_joined(
                        player_monitor_thread_running['server'], player)
            if left_players:
                for player in left_players:
                    ph.print_respect_cli(f"{player} {Fore.LIGHTRED_EX}left")
                    player_left(
                        player_monitor_thread_running['server'], player)

            previous_players = players.copy()
        time.sleep(1/tps)


def player_monitor_cmd(*args, parent=None):
    global player_monitor_thread_running
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)

    parser.add_argument('server', nargs='?', type=str,
                        default=None)
    args = parser.parse_args(args)
    # If the command is run while a monitor is running, disable that monitor
    # If the user provides a server, enable a monitor for that server, regardless of if a current monitor needs to be disabled
    if player_monitor_thread_running is not False:
        # Disable player monitor
        # Wait for thread to finish
        player_monitor_thread_running['running'] = False
        player_monitor_thread_running['thread'].join()
        player_monitor_thread_running = False
        print(f"{Fore.YELLOW}Player monitor stopped")
        if args.server is None:
            # No alternate server provided
            return

    # Continue to enable player monitor
    server_handler = command.SelectedServerHandler()
    server = server_handler.handle_address(args.server, tuple=True)
    t = threading.Thread(target=player_monitor_thread, daemon=True)
    player_monitor_thread_running = {
        'server': server,
        'name': a2s.info(server).server_name,
        'thread': t,
        'running': True
    }

    player_monitor_thread_running['thread'].start()


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
    print(get_player_names(('198.244.176.107', 27015)))
