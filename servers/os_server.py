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
if "os_storage" not in os.listdir("/opt"):
    os.mkdir("/opt/os_storage")

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
        ack(srvcon, 0)
#        client_list.append(srvcon)
        thread_client = task.Thread(target=client_start, args=[srvcon])
        thread_client.start()


def client_start(client):
    while True:
        try:
            path = client.recv(1024).decode("utf-8")
        except:
            break
        if path:
            if "#list" in path:
                if " " in path:
                    temp, path = path.split(" ")
                    if path[len(path) - 1] != "/":
                        path += "/"
                else:
                    path = ""
                try:
                    reply = "!"
                    for item in os.listdir(home+path):
                        reply += item+"\n"
                    client.send(reply.encode("utf-8"))
                except:
                    client.send("!Directory does not exist".encode("utf-8"))
                continue
            else:
                try:
                    send_file(client, path)
                except Exception as e:
                    print(f"error sending file to requestor: {e}")
                    client.send("!File not found".encode("utf-8"))
                time.sleep(0.5)
        else:
            break

def receive_file(client, path):
    data_received = 0
    part_size = 4096
    check = client.recv(1).decode("utf-8")
    if check == "!":
        data = client.recv(part_size).decode("utf-8")
        print(data)
        return
    else:
        packet_size = check
    packet_size += client.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    ack(client, 1)
    if not path:
        path = input("file name? >>> ")
    with open(download+path, "wb") as file:
        print(f"opening file at {download}{path}")
        while data_received < packet_size:
            remaining_data = packet_size - data_received
            print(f"starting download. chunk size: {part_size}")
            remaining_data = min(part_size, remaining_data)
            part = client.recv(remaining_data)
            print(f"receiving {len(part)} bytes")
            if not part:
                break
            file.write(part)
            data_received += len(part)
    print("file downloaded\nfile written to path")
    ack(client, 1)

def send_file(client, path):
    with open(home+path, "rb") as file:
        file.seek(0, 2)
        file_size = file.tell()
    head = str(file_size).zfill(header_size)
    print(f"file size {header_size}, sending...")
    client.send(str(head).encode("utf-8"))
    ack(client, 0)
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
    ack(client, 0)

def send(client, data):
    head = str(len(data + is_flagged)).zfill(header_size)
    data = head + is_flagged + data
    client.send(data.encode("utf-8"))
    ack(client, 0)

def receive(client):
    data_received = b''
    print("receiving header..")
    packet_size = server.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    print(f"header size is: {packet_size}")
    while len(data_received) < packet_size:
        data_received += server.recv(packet_size - len(data_received))
        print(f"data being received: {packet_size} | {len(data_received)} = {data_received}")
    ack(client, 1)
    data_received = data_received.decode("utf-8")
    return data_received

def ack(client, state):
    if not state:
        ack_acpt = client.recv(3).decode("utf-8")
    else:
        client.send(ACK.encode('utf-8'))

init_server()
