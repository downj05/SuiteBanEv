import time
import keyboard
import mouse


def swinger(*args):
    """
    Swings players weapon automatically with configurable delay,
    action (left or right click) and count (infinite by default)
    """

    # Args: -d <delay> -a <action> -c <count>
    # Defaults: delay=0.8, action=left, count=inf

    # Parse args
    delay = 0.8
    action = "left"
    count = float("inf")
    exit_key = "q"

    for i, arg in enumerate(args):
        if arg == "-d":
            delay = float(args[i+1])
        elif arg == "-a":
            action_arg = args[i+1].lower()
            if action_arg in ['l', 'left', 'left_click']:
                action = "left"
            elif action_arg in ['r', 'right', 'right_click']:
                action = "right"
            else:
                raise ValueError(
                    f"Invalid action argument: {action_arg}. Must be one of 'left', 'right', 'left_click', 'right_click'")

        elif arg == "-c":
            count = int(args[i+1])

    print(f"Swinging every {delay} seconds with {action} click", end="")
    if count != float("inf"):
        print(f" for {count} swings")
    else:
        print(" indefinitely")

    print(f"Press {exit_key} at anytime to stop")
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
        if i % int(delay / TICK) == 0:
            mouse.click(action)
            c += 1

        if c >= count:
            print(f"Swinger finished after {count} swings")
            break
        if keyboard.is_pressed(exit_key):
            print("Swinger interrupted")
            break


if __name__ == '__main__':
    args = '-d 0.8 -a left -c 10'.split()
    swinger(*args)
