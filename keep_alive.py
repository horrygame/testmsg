import requests
import time

while True:
    try:
        requests.get("https://testmsg-562i.onrender.com")
        print("Server pinged")
    except:
        pass
    time.sleep(300)  # Каждые 5 минут
