import keyboard
import mouse
import time


def afk():
    while True:
        if keyboard.is_pressed("q"):
            break


if __name__ == "__main__":
    while True:
        if keyboard.is_pressed("e"):
            print(mouse.get_position())
            time.sleep(0.5)
        if keyboard.is_pressed("q"):
            break
        time.sleep(0.1)
