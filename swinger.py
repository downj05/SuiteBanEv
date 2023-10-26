import time
import keyboard
import mouse

W = 3
for i in range(0, W):
    print(f"Starting in {W-i}...")
    time.sleep(1)

# # Main loop
while True:
    # Check if the 'q' key is pressed
    if keyboard.is_pressed("q"):
        break  # Exit the loop if 'q' is pressed
    mouse.click("right")
    time.sleep(2)

# while True:
#     keyboard.press("f")
#     time.sleep(0.05)
#     keyboard.release("f")
#     if keyboard.is_pressed("q"):
#         break
#     time.sleep(0.05)


print("Script terminated.")
