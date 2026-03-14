import json
import os
from datetime import datetime, timedelta

OPTIONS_FILE = "/data/options.json"

# Load Add-on options
if os.path.exists(OPTIONS_FILE):
    with open(OPTIONS_FILE) as f:
        OPTIONS = json.load(f)
else:
    OPTIONS = {
        "pin": "100578",
        "latitude": 40.325031,
        "longitude": 21.787019,
        "schedule": {}
    }

schedule = OPTIONS.get("schedule", {})

def next_event(action):
    """Return next datetime for 'login' or 'logout'"""
    now = datetime.now()
    for i in range(7):
        day = (now.weekday() + i) % 7
        str_day = str(day)
        if str_day in schedule:
            time_str = schedule[str_day][action]  # "HH:MM"
            hour, minute = map(int, time_str.split(":"))
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=i)
            if target > now:
                return target
    return None

def run_scheduler():
    """Optional background scheduler placeholder if needed"""
    while True:
        # Here you could put retry/failsafe logic
        pass
