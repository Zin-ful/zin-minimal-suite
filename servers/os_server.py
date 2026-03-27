#!/bin/env python3
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import base64
import threading as task
import time

client_list = []

"""default vars"""

header_size = 100
LADDR = "0.0.0.0"
PORT = 25415
ACK = "ack"
home = "/opt/os_storage/"

init_system = {"misc": "Misc", "orc": "OpenRC", "r6": "R6", "runit": "Runit", "sysd - warning: SystemD has decided to implement age verification.": "SystemD"}

if "os_storage" not in os.listdir("/opt"):
    os.mkdir("/opt/os_storage")

for i, j in init_system.items():
    if j not in os.listdir(home):
        os.mkdir(home+j)

server = netcom.socket(ipv4, tcp)

"""server junk"""

def init_server():
    global server
    if server == None:
        server = netcom.socket(ipv4, tcp)
    print(f"binding server to {LADDR} {PORT}")
    server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
    server.bind((LADDR, PORT))
    print("server created and listening")
    while True:
        server.listen()
        srvcon, srvcon_ip = server.accept()
        thread_client = task.Thread(target=client_start, args=[srvcon])
        thread_client.start()


def client_start(client):
    
    while True:
        msg = ""
        choices = []
        for key, value in init_system.items():
            msg += f"{key}\n"
            choices.append(key)
        msg = "Choose your init system:\n" + msg
        send(client, msg)
        while True:
            choice = receive(client)
            if choice not in choices:
                send(client, "Invalid choice, choose from the list.")
                continue
            else:
                break
        print("os choosen")
        msg = ""
        i = 0
        choices = []
        path = init_system[choice]
        for item in os.listdir(home + path):
            msg += f"{i}. {item}\n"
            choices.append(item)
            i += 1
        msg = "Choose operating system:\n" + msg
        send(client, msg)
        while True:
            choice = receive(client)
            try:
                choice = int(choice.strip())
                name = choices[choice]
                break
            except Exception as e:
                print(str(e))
                name = choice
                if name not in choices:
                    send(client, "Invalid choice.")
                    continue
                break
            print("os choosen")
            break
        path = path + "/" + name
        send(client, "!")
        time.sleep(0.1)
        send_file(client, path)
        print("ending looping")

def send_file(client, path):
    with open(home+path, "rb") as file:
        file.seek(0, 2)
        file_size = file.tell()
    head = str(file_size).zfill(header_size)
    print(f"file size {header_size}, sending...")
    client.send(str(head).encode("utf-8"))
    with open(home+path, "rb") as file:
        i = 0
        while True:
            part = file.read(4096)
            if not part:
                break
            print(f"sending part {i}")
            client.send(part)
            i += 1
    print("file sent")
    send(client, "Returning to main menu")

def send(client, data):
    print(f"sending:\n{data}")
    head = str(len(data)).zfill(header_size)
    data = head + data
    client.send(data.encode("utf-8"))

def receive(client):
    data_received = b''
    print("receiving header..")
    packet_size = client.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    print(f"header size is: {packet_size}")
    while len(data_received) < packet_size:
        data_received += client.recv(packet_size - len(data_received))
        print(f"data being received: {packet_size} | {len(data_received)} = {data_received}")
    data_received = data_received.decode("utf-8")
    return data_received

init_server()
