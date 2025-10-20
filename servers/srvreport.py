from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
from time import sleep

import os

port = 52311
server = netcom.socket(ipv4, tcp)
print("socket created")
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
print("set socket options")
server.bind(("0.0.0.0", port))
print(f"bound to {port}")
connections = {}

conf = "/etc/zinapps/report"
if not "zinapps" in os.listdir("/etc"):
    os.mkdir("/etc/zinapps")
if not "report" in os.listdir("/etc/zinapps"):
    os.mkdir("/etc/zinapps/report")

def init():
    while True:
        try:
            print("listening...")
            server.listen(20)
            client, client_ip = server.accept()
            print(f"client accepted: {client_ip}")
            connections.update({client_ip: client})
            thread_client = task.Thread(target=client_start, args=[client_ip, client])
            thread_client.start()
        except Exception as e:
            print(e)

def client_start(client_ip, client):
    ack = client.recv(3).decode("utf-8")
    print("acked")
    if ack.strip() != "ack":
        print("client is out of sync, exiting")
        return
    while True:
        try:
            client.send("ack".encode("utf-8"))
            sleep(10)
            client.recv(3)
            sleep(10)
        except Exception as e:
            print(e)
            client.close()
            break
        with open(conf+"/report.txt", "w") as file:
            for addr, data in connections:
                file.write(addr+"\n")

init()