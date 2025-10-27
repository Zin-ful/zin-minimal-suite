from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import base64
import threading as task
import time

client_list = []

"""default vars"""

srv = 1
cli = 1
header_size = 100
IP = input("Ip addr? (enter for localhost)\n>>> ")
LADDR = "0.0.0.0"
PORT = 25415
ACK = "ack"
home = "/home/"
   
client = netcom.socket(ipv4, tcp)
server = netcom.socket(ipv4, tcp)

if IP == "nosrv":
    srv = 0
    IP = input("server not started, now enter the IP address of where you want to connect:\n>>> ")
elif IP == "nocli":
    cli = 0

if cli:
    download = input("folder to download to? >>> ")
    if download[len(download) - 1] != "/":
        print("no / added to the end of the directory.")
        print("if you dont add one, youll need to add one when downloading a file.")
        tmp = input("add one? >>> ")
        if "y" in tmp:
            download += "/"
        del tmp
else:
    download = None 

if not IP:
    IP = "localhost"


"""server junk"""

def init_server():
    global server
    if server == None:
        server = netcom.socket(ipv4, tcp)
    print(f"binding server to {LADDR} {PORT}")
    server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
    server.bind((LADDR, PORT))
    print("server created and listening")
    if cli:
        init_client()
    while True:
        server.listen()
        srvcon, srvcon_ip = server.accept()
        ack(srvcon, 0)
        client_list.append(srvcon)
        thread_client = task.Thread(target=client_start, args=[srvcon])
        thread_client.start()

def client_start(client):
    while True:
        path = client.recv(1024).decode("utf-8")
        if path:
            print(path)
            try:
                send_file(client, path)
            except Exception as e:
                print(f"error sending file to requestor: {e}")
            time.sleep(0.5)

def client_shell(client):
    while True:
        print("input the path of a file to download it")
        print("The path starts from '/home'\n\n")
        inp = input(">>> ")
        path = input("file name? >>> ")
        client.send(inp.encode("utf-8"))
        receive_file(client, path)

def init_client():
    global client
    if client == None:
        client = netcom.socket(ipv4, tcp)
    print(f'trying {IP}:{PORT}')
    try:
        client.connect((IP, PORT))
        print("connected, moving to shell..")
        client.send(ACK.encode("utf-8"))
        client_shell(client)
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

def receive_file(client, path):
    data_received = 0
    part_size = 4096
    packet_size = client.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    ack(client, 1)
    with open(download+path, "wb") as file:
        print(f"opening file at {download}{path}")
        while data_received < packet_size:
            data_received = packet_size - data_received
            print(f"starting download. chunk size: {part_size}")
            part = client.recv(min(part_size, data_received))
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
if srv:
    init_server()
else:
    init_client()