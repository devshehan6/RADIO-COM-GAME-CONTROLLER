import serial
import time
from pynput.keyboard import Controller, Key, KeyCode

PORT = "COM6"
BAUD_RATE = 115200

keyboard = Controller()

# Serial bit order: b, c, a, d
# b = Right, c = Forward, a = Left, d = Backward
KEY_MAP = {
    "R": Key.right,
    "F": Key.up,
    "L": Key.left,
    "B": Key.down
}

pressed_keys = set()

def update_keys(signal):
    global pressed_keys

    new_keys = set()

    if signal[0] == "0":
        # new_keys.add(Key.right)
        new_keys.add(KeyCode.from_char('d'))

    if signal[1] == "0":
        # new_keys.add(Key.up)
        new_keys.add(KeyCode.from_char('w'))

    if signal[2] == "0":
        # new_keys.add(Key.left)
        new_keys.add(KeyCode.from_char('a'))

    if signal[3] == "0":
        # new_keys.add(Key.down)
        new_keys.add(KeyCode.from_char('s'))

    # Release keys that are no longer active
    for key in pressed_keys - new_keys:
        keyboard.release(key)

    # Press newly active keys
    for key in new_keys - pressed_keys:
        keyboard.press(key)

    pressed_keys = new_keys

try:
    with serial.Serial(PORT, BAUD_RATE, timeout=0.1) as ser:
        time.sleep(2)
        ser.reset_input_buffer()

        print("RC Game Controller Ready!")
        print("Focus your game window. Press Ctrl+C to stop.")

        while True:
            line = ser.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            # Accept inputs such as 1, 1, 1, 1
            bits = line.replace(",", "").replace(" ", "")

            if len(bits) == 4 and all(
                bit in "01" for bit in bits
            ):
                update_keys(bits)
                print(
                    f"{bits} | "
                    f"Active: {''.join(
                        name for name, key in [
                            ('R', Key.right),
                            ('F', Key.up),
                            ('L', Key.left),
                            ('B', Key.down)
                        ] if key in pressed_keys
                    ) or 'None'}"
                )

except KeyboardInterrupt:
    print("\nController stopped.")

except Exception as e:
    print("Error:", e)

finally:
    for key in list(pressed_keys):
        keyboard.release(key)
