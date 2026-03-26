#!/bin/env python3
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import base64
import threading as task
import time

"""default vars"""
header_size = 100
IP = input("Ip addr? (enter for localhost)\n>>> ")
ACK = "ack"
home = "/home/"
   
client = netcom.socket(ipv4, tcp)
server = netcom.socket(ipv4, tcp)

download = input("folder to download to? >>> ")
if download[len(download) - 1] != "/":
    print("no / added to the end of the directory.")
    print("if you dont add one, youll need to add one when downloading a file.")
    tmp = input("add one? >>> ")
    if "y" in tmp:
        download += "/"
    del tmp
elif not download:
    download = home
if not IP:
    IP = "localhost"

def client_shell(client):
    while True:
        print("input the path of a file to download it")
        print("The path starts from '/home/'\n\n")
        inp = input("(#list to check directories) >>> ")        
        client.send(inp.encode("utf-8"))
        receive_file(client, None)

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
oinit_client()
