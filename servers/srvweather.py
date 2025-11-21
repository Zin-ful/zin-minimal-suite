import requests
import threading
import os
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
from time import sleep
from datetime import datetime

conf_path = "/opt/zinapp/weather"
if not "zinapp" in os.listdir("/opt"):
    os.mkdir("/opt/zinapp")
if not "weather" in os.listdir("/opt/zinapp"):
    os.mkdir("/opt/zinapp/weather")

port = 49021
server = netcom.socket(ipv4, tcp)
print("socket created")
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
print("set socket options")
server.bind(("0.0.0.0", port))
print(f"bound to {port}")
connections = {}

threads = {}

recent_time = 0

url = "https://api.weather.gov/alerts/active?area="
fetch_cmd = ["curl", "-s", url]


print("listening...")
server.listen(20)

def init():
    while True:
        try:
            client, client_ip = server.accept()
            print(f"client accepted: {client_ip}")
            thread_client = task.Thread(target=client_start, args=[client, client_ip])
            thread_client.start()
        except Exception as e:
            print(e)

def client_start(client, client_ip):
    state = client.recv(2).decode("utf-8")
    state = state.upper()
    wait_time = client.recv(10).decode("utf-8")

    if wait_time:
        wait_time = int(wait_time)
    client_count = len(threads.keys())
    if not client_count:
        client_count = 0
    pause = 0
    client_exists = 1

    threads.update({client: {"pause": pause, "exists": client_exists}})
    alert_thread = task.Thread(target=get_alert, args=[state, wait_time, 0, client])
    alert_thread.start()

    print(state, wait_time)
    client.send("*".encode("utf-8"))
    while threads[client]["exists"]:
        try:
            alert_request = client.recv(2).decode("utf-8")
            if alert_request:
                while threads[client]["pause"]:
                    sleep(0.1)
                    print("requesting paused.. waiting")
                if alert_request == "*":
                    num = len(os.listdir(f"{conf_path}/{state}"))
                    if not num:
                        client.send("%".encode("utf-8"))
                        continue
                    with open(f"{conf_path}/{state}/alert_{num - 1}.txt", "r") as file:
                        alert = file.read()
                    print("sending time")
                    print(f"sending alert number {num - 1}")
                    client.send(f"{recent_time}%{alert}".encode("utf-8"))
                else:
                    state = alert_request.upper()
                    get_alert(state, wait_time, 1, client)
                    num = len(os.listdir(f"{conf_path}/{state}"))
                    if not num:
                        client.send("%".encode("utf-8"))
                        continue
                    print(f"location request, sending alert {num - 1}")
                    with open(f"{conf_path}/{state}/alert_{num - 1}.txt", "r") as file:
                        alert = file.read()
                    client.send(f"{recent_time}%{alert}".encode("utf-8"))
                    
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            print("disconnecting client")
            threads[client]["exists"] = 0
            client_end(client)
            alert_thread.join()
            break
            
def client_end(client):
    print("closing client")
    client.close()

def save(state, header, event, details, properties, num):
    with open(f"{conf_path}/{state}/alert_{num}.txt", "a") as file:
        file.write(f"{header}\n@!\n{event}\n!@\n{details}\n##\n")

def get_ftime(state, alert_number):
    global recent_time
    creation_time = datetime.fromtimestamp(os.path.getctime(f"{conf_path}/{state}/alert_{alert_number - 1}.txt"))
    recent_time =  f"{creation_time.month}-{creation_time.day}-{creation_time.hour}-{creation_time.minute}"

def get_time():
    global recent_time
    current_time = datetime.now()
    recent_time = current_time.strftime("%m-%d %H:%M")

def get_alert(state, wait_time, temp, client):
    if state not in os.listdir(conf_path):
        os.mkdir(f"{conf_path}/{state}")
    while threads[client]["exists"]:
        num = len(os.listdir(f"{conf_path}/{state}"))
        if not num:
            num = 0
        print("pausing client")
        threads[client]["pause"] = 1
        try:
            print("getting alert data")
            weatherdata = requests.get(url+state)
            errors = weatherdata.raise_for_status()
            data = weatherdata.json()
            alert_data = data.get("features", [])
            if not alert_data:
                return
            for alert in alert_data:
                properties = alert.get("properties", {})
                event = properties.get("event", "unknown event")
                headline = properties.get("headline", "no headline")
                details = properties.get("description", "no description")
                effective = properties.get("effective")
                save(state, headline, event, details, properties, num)
            get_time()
        except requests.exceptions.RequestException as e:
            get_ftime(state, num)
            print("unpausing client")
            threads[client]["pause"] = 0
            print("error. waiting..")
            sleep(wait_time // 4)
            continue
        if temp:
            break
        print("unpausing client")
        threads[client]["pause"] = 0
        print(f"alert gotten. written to alert_{num - 1}.txt waiting...")
        sleep(wait_time)
    print(f"ending thread {client_name}")
        
init()
