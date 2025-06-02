from flask import Flask, request
import os
import subprocess  # For notification
import platform

app = Flask(__name__)
LOG_PATH = "received_logs.txt"

def notify_user(message):
    if platform.system() == "Windows":
        # Using Toast notifications on Windows
        import win10toast
        toaster = win10toast.ToastNotifier()
        toaster.show_toast("Log Received", message, duration=5)
    else:
        # Linux/macOS notification example
        subprocess.run(['notify-send', "Log Received", message])

@app.route("/upload", methods=["POST"])
def upload_log():
    data = request.data.decode("utf-8")
    with open(LOG_PATH, "a") as f:
        f.write(data + "\n")
    notify_user(f"New log data received ({len(data)} chars)")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

