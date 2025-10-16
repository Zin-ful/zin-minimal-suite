from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import base64
import threading

client_list = []

"""default vars"""
header_size = 100
IP = input("Ip addr? (enter for localhost)\n>>> ")
if not IP:
    IP = "localhost"
LADDR = "0.0.0.0"
PORT = 25415

path = "/home/"

client = netcom.socket(ipv4, tcp)
server = netcom.socket(ipv4, tcp)

"""server junk"""

def init_server():
    if server == None:
        server = netcom.socket(ipv4, tcp)
    print(f"binding server to {LADDR} {PORT}")
    server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
    server.bind((LADDR, PORT))
    print("server created and listening")
    init_client()
    while True:
        server.listen()
        client, client_ip = server.accept()
        ack(client, 0)
        client_list.append(client)
        thread_client = task.Thread(client_start, args=[client])
        thread_client.start()

def client_start(client):
    while True:
        path = client.recv(1024).decode("utf-8")
        try:
            send_file(path)
        except Exception as e:
            print(f"error sending file to requestor: {e}")

def client_shell(client):
    print("input the path of a file to download it")
    print("The path starts from '/home'\n\n")
    inp = input(">>> ")
    client.send(inp.encode("utf-8")
    receive_file()

def init_client():
    global ack, server
    if client == None:
        client = netcom.socket(ipv4, tcp)
    print(f'trying {IP}:{PORT}')
    try:
        client.connect((IP, PORT))
        print("connected, moving to shell..")
        client.send(ACK.encode("utf-8"))
        return
    except Exception as e:
        print(f"error: {e}")
        print("lost connection to server. do you want to retry?")
        inp = input(">>> ")
        if "y" in inp:
            if client.fileno() != -1:
                print("attempting shutdown...")
                try:
                    client.shutdown(netcom.SHUT_RDWR)
                except OSError:
                    print("No endpoint to shutdown. Closing server")
                client.close()
            print("retrying... (waiting for server, be patient)")
            init_client()
        else:
            client.close()
            exit()

def receive_file():
    part_size = 4096
    packet_size = server.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    ack(1)
    with open(path, "wb") as file:
        while data_received < packet_size:
            data_received = packet_size - data_received
            part = server.recv(min(part_size, data_received))
            if not part:
                break
            file.write(part)
            data_received += len(part)
    ack(1)

def send_file(path):
    with open(path, "rb") as file:
        file.seek(0, 2)
        file_size = file.tell()
    head = str(file_size).zfill(header_size)
    print(f"file size {header_size}, sending...")
    server.send(str(head).encode("utf-8"))
    ack(0)
    with open(path, "rb") as file:
        i = 0
        while True:
            part = file.read(4096)
            if not part:
                break
            print(f"sending part {i}")
            server.send(part)
            i += 1
    ack(0)

def send(screens, data, encoded):
    head = str(len(data + is_flagged)).zfill(header_size)
    data = head + is_flagged + data
    server.send(data.encode("utf-8"))
    ack(0)

def receive(screens, encoded):
    data_received = b''
    print("receiving header..")
    packet_size = server.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    print(f"header size is: {packet_size}")
    while len(data_received) < packet_size:
        data_received += server.recv(packet_size - len(data_received))
        print(f"data being received: {packet_size} | {len(data_received)} = {data_received}")
    ack(1)
    data_received = data_received.decode("utf-8")
    return data_received

def ack(state):
    if not state:
        ack_acpt = server.recv(3).decode("utf-8")
    else:
        server.send(ACK.encode('utf-8'))