import requests
import threading
import os
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
from time import sleep

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
    alert_thread = task.Thread(target=get_alert, args=[state, wait_time, 0])
    alert_thread.start()
    print(state, wait_time)
    client.send("*".encode("utf-8"))
    while True:
        try:
            alert_request = client.recv(2).decode("utf-8")
            if alert_request:
                if alert_request == "*":
                    num = len(os.listdir(f"{conf_path}/{state}"))
                    if not num:
                        client.send("#none".encode("utf-8"))
                        continue
                    with open(f"{conf_path}/{state}/alert_{num - 1}.txt", "r") as file:
                        alert = file.read()
                    print(f"alert_{num - 1}", alert)
                    client.send(alert.encode("utf-8"))
                else:
                    state = alert_request.upper()
                    get_alert(state, wait_time, 1)
                    num = len(os.listdir(f"{conf_path}/{state}"))
                    if not num:
                        client.send("#none".encode("utf-8"))
                        continue
                    with open(f"{conf_path}/{state}/alert_{num - 1}.txt", "r") as file:
                        alert = file.read()
                    print(f"alert_{num - 1}", alert)
                    client.send(alert.encode("utf-8"))
                    
        except (BrokenPipeError, ConnectionResetError):
            client_end(client)
            alert_thread.join()

def client_end(client):
    print("closing client")
    client.close()

def save(state, header, event, details, properties, num):
    with open(f"{conf_path}/{state}/alert_{num}.txt", "a") as file:
        file.write(f"{header}\n!@{event}\n@!{details}\n##\n")

def get_alert(state, wait_time, temp):
    if state not in os.listdir(conf_path):
        os.mkdir(f"{conf_path}/{state}")
    num = len(os.listdir(f"{conf_path}/{state}"))
    if not num:
        num = 0
    while True:
        try:
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
        except requests.exceptions.RequestException as e:
            continue
            sleep(wait_time // 4)
        if temp:
            break
        sleep(wait_time)
        
init()
