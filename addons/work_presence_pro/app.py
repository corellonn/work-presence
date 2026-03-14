from flask import Flask, jsonify
import threading, time
from datetime import datetime
from scheduler import next_event, run_scheduler
from presence import send_presence
from stats import log_event
import json, os

# Load options
OPTIONS_FILE = "/data/options.json"
if os.path.exists(OPTIONS_FILE):
    with open(OPTIONS_FILE) as f:
        OPTIONS = json.load(f)
else:
    OPTIONS = {
        "pin": "100578",
        "latitude": 40.325031,
        "longitude": 21.787019
    }

PIN = OPTIONS["pin"]
LAT = OPTIONS["latitude"]
LON = OPTIONS["longitude"]

status = "idle"

app = Flask(__name__)

# -----------------------------
# Worker Thread
# -----------------------------
def worker():
    global status
    while True:
        now = datetime.now()
        login_time = next_event("login")
        logout_time = next_event("logout")

        # AUTO LOGIN
        if login_time and abs((login_time - now).total_seconds()) < 30:
            if send_presence(PIN, "in", LAT, LON):
                log_event("login")
                status = "login success"
                print(f"[{datetime.now()}] Auto LOGIN executed")

        # AUTO LOGOUT
        if logout_time and abs((logout_time - now).total_seconds()) < 30:
            if send_presence(PIN, "out", LAT, LON):
                log_event("logout")
                status = "logout success"
                print(f"[{datetime.now()}] Auto LOGOUT executed")

        time.sleep(20)

# -----------------------------
# API Routes
# -----------------------------
@app.route("/status")
def api_status():
    return jsonify({
        "status": status,
        "next_login": str(next_event("login")),
        "next_logout": str(next_event("logout"))
    })

@app.route("/login")
def manual_login():
    global status
    if send_presence(PIN, "in", LAT, LON):
        log_event("login")
        status = "login success"
        print(f"[{datetime.now()}] Manual LOGIN executed")
        return "login success"
    else:
        status = "login failed"
        return "login failed", 500

@app.route("/logout")
def manual_logout():
    global status
    if send_presence(PIN, "out", LAT, LON):
        log_event("logout")
        status = "logout success"
        print(f"[{datetime.now()}] Manual LOGOUT executed")
        return "logout success"
    else:
        status = "logout failed"
        return "logout failed", 500

# -----------------------------
# Start Threads
# -----------------------------
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=run_scheduler, daemon=True).start()

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099)
