import requests
import time

API="https://hr.balkanelectric.gr/api/presence"

def send_presence(pin, action, lat, lon):

    payload={
        "type":action,
        "pin":pin,
        "lat":lat,
        "lon":lon
    }

    retries=5

    for i in range(retries):

        try:

            r=requests.post(API,json=payload,timeout=10)

            if r.status_code==200:
                return True

        except:
            pass

        time.sleep(10)

    return False
