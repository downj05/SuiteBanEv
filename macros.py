import time
import keyboard
import mouse
import argparse


def swinger(*args, parent=None):
    """
    Swings players weapon automatically with configurable delay,
    action (left or right click) and count (infinite by default)
    """

    # Args: -d <delay> -a <action> -c <count>
    # Defaults: delay=0.8, action=left, count=inf
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)
    parser.add_argument('-d', '--delay', type=float,
                        help='Delay between swings in seconds (default: 0.8)', default=0.8)
    parser.add_argument('-a', '--action', type=str,
                        help='Mouse click action to perform (left/l, right/r) (default: left)', default='left')
    parser.add_argument('-c', '--count', type=int, help='Number of swings (default: infinite swings)',
                        default=float('inf'))
    parser.add_argument('-e', '--exit', type=str, help='Key to exit (default: q)',
                        default='q')
    args = parser.parse_args(args)

    if args.action == 'left' or args.action == 'l':
        action = 'left'
    elif args.action == 'right' or args.action == 'r':
        action = 'right'
    else:
        raise ValueError(f"Invalid action {args.action}")

    print(
        f"Swinging every {args.delay} seconds with {args.action} click", end="")

    if args.count != float("inf"):
        print(f" for {args.count} swings")
    else:
        print(" indefinitely")

    print(f"Press {args.exit} at anytime to stop")
    # Count down
    COUNTDOWN = 3
    for i in range(0, COUNTDOWN):
        print(f"Starting in {COUNTDOWN-i}...")
        time.sleep(1)

    # Main loop
    i = 0  # Timer counter
    c = 0  # Swing counter
    TICK = 0.03  # 30 times per second
    while True:
        time.sleep(TICK)  # Sleep to prevent CPU hogging, 30 times per second
        i += 1
        # If the timer counter is divisible by the delay, click
        if i % int(args.delay / TICK) == 0:
            mouse.click(action)
            c += 1

        if c >= args.count:
            print(f"Swinger finished after {args.count} swings")
            break
        if keyboard.is_pressed(args.exit):
            print("Swinger interrupted")
            break


def wiggle(*args, parent):
    parser = argparse.ArgumentParser(
        prog=parent.name, add_help=False, usage=parent.usage)
    parser.add_argument('-d', '--delay', type=float,
                        help='Delay between leaning a different direction (default: 0.38)', default=0.38)
    parser.add_argument('-kt', '--key-time', type=float,
                        help='Time to hold the key for (default: 0.05)', default=0.05)
    parser.add_argument('-t', '--type', type=str,
                        choices=['cuffs', 'handcuffs', 'cable', 'cabletie', 'inf', 'infinite'], default='inf', help='determines how many times to wiggle depending on what you are trapped with (default: infinite)')
    parser.add_argument('-e', '--exit', type=str,
                        help='Key to exit (default: q)', default='q')
    args = parser.parse_args(args)

    types = {
        128: (['cuffs', 'handcuffs'], 'Handcuff'),
        64: (['cable', 'cabletie'], 'Cable Tie'),
        float('inf'): (['inf', 'infinite'], 'Endless')
    }

    # Resolve string choice to wiggle count
    print(f"Wiggling in ", end='')
    for k, i in types.items():
        if args.type in i[0]:
            count = k
            print(f"{i[1]} mode ({k} times) with {args.delay} second delay")
            break

    COUNTDOWN = 3
    for i in range(0, COUNTDOWN):
        print(f"Starting in {COUNTDOWN-i}...")
        time.sleep(1)

    # Main loop
    i = 0  # Timer counter
    c = 0  # Wiggle counter
    TICK = 0.03  # 30 times per second
    flip = False
    while True:
        time.sleep(TICK)  # Sleep to prevent CPU hogging, 30 times per second
        i += 1
        # If the timer counter is divisible by the delay, wiggle 1 way
        if i % int(args.delay / TICK) == 0:
            if flip:
                keyboard.press('e')
                keyboard.release('q')
            else:
                keyboard.press('q')
                keyboard.release('e')

            flip = not flip
            c += 1
        if c >= count:
            print(f"{parent.name} finished after {count} swings")
            break
        if keyboard.is_pressed(args.exit):
            print("Wiggle interrupted")
            break


if __name__ == '__main__':
    args = '-d 0.8 -a left -c 10'.split()
    swinger(*args)
