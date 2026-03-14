from flask import Flask, jsonify, render_template_string
import threading, time
from datetime import datetime
from scheduler import next_event, run_scheduler
from presence import send_presence
from stats import log_event
import json, os
from presence import send_presence
from stats import log_event
from scheduler import next_event

app = Flask(__name__)

PIN = "100578"
LAT = 40.325031
LON = 21.787019

status = "idle"

# Panel route για Home Assistant sidebar
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Work Presence Pro</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            h2 { color: #2c3e50; }
            .status { margin: 10px 0; font-weight: bold; }
            button { margin: 5px; padding: 10px 15px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>Work Presence Pro</h2>
        <div class="status">STATUS: <span id="status">loading...</span></div>
        <div>Next Login: <span id="next_login">--:--</span></div>
        <div>Next Logout: <span id="next_logout">--:--</span></div>
        <div>
            <button onclick="manual('login')">Manual IN</button>
            <button onclick="manual('logout')">Manual OUT</button>
        </div>
        <div>
            <h3>Work Statistics</h3>
            <div id="stats">Loading...</div>
        </div>
        <script>
            async function fetchStatus() {
                try {
                    let res = await fetch("/status");
                    let data = await res.json();
                    document.getElementById("status").innerText = data.status;
                    document.getElementById("next_login").innerText = data.next_login;
                    document.getElementById("next_logout").innerText = data.next_logout;
                    document.getElementById("stats").innerText = data.work_hours || "No data";
                } catch(e) {
                    console.log(e);
                }
            }

            async function manual(action){
                try {
                    await fetch("/" + action);
                    fetchStatus();
                } catch(e){
                    console.log(e);
                }
            }

            setInterval(fetchStatus, 3000);
            fetchStatus();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)



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

