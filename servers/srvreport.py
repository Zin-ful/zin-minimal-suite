from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
from time import sleep

import os

port = 23621
server = netcom.socket(ipv4, tcp)
print("socket created")
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
print("set socket options")
server.bind(("0.0.0.0", port))
print(f"bound to {port}")
connections = {}

interval = 5

conf = "/opt/zinapp/report"
if not "zinapp" in os.listdir("/opt"):
    os.mkdir("/opt/zinapp")
if not "report" in os.listdir("/opt/zinapp"):
    os.mkdir("/opt/zinapp/report")

print("listening...")
server.listen(20)

def init():
    while True:
        try:
            client, client_ip = server.accept()
            print(f"client accepted: {client_ip}")
            connections.update({client_ip: client})
            thread_client = task.Thread(target=client_start, args=[client, client_ip])
            thread_client.start()
        except Exception as e:
            print(e)

def client_start(client, client_ip):
    print(interval)
    client.settimeout(interval + 5)
    ack = client.recv(3).decode("utf-8")
    client_interval = str(interval).zfill(4)
    if len(client_interval) > 4:
        client_interval = "0030"
    client.send(client_interval.encode("utf-8"))
    print("interval sent")
    if ack.strip() != "ack":
        print("client is out of sync, exiting")
        client_end(client)
        return
    while True:
        try:
            client.send("ack".encode("utf-8"))
            sleep(interval)
            client.recv(3)
            sleep(interval)
        except (BrokenPipeError, ConnectionResetError):
            client_end(client)
        with open(conf+"/report.txt", "w") as file:
            for addr, data in connections:
                file.write(addr+"\n")

def client_end(client):
    print("closing client")
    client.close()
init()