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


if __name__ == '__main__':
    args = '-d 0.8 -a left -c 10'.split()
    swinger(*args)
