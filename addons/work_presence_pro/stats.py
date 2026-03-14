import json
from datetime import datetime

FILE="/data/work_stats.json"

def log_event(action):

    try:
        data=json.load(open(FILE))
    except:
        data=[]

    data.append({
        "time":datetime.now().isoformat(),
        "action":action
    })

    json.dump(data,open(FILE,"w"))
