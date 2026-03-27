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
PORT = 25415
ACK = "ack"
home = "/home/"
   
client = netcom.socket(ipv4, tcp)
server = netcom.socket(ipv4, tcp)

download = input("folder to download to? >>> ")
if download[len(download) - 1] != "/":
    print("no / added to the end of the directory.")
    print("if you dont add one, youll need to add one when downloading a file.")
    tmp = input("add one? >>> ")
    if "y" in tmp or not tmp:
        download += "/"
elif not download:
    download = home
if not IP:
    IP = "localhost"

def client_shell(client):
    while True:
        data = receive(client)
        if data[0] == "!":
            receive_file(client, None)
        else:
            print(data)
        inp = input(">>> ")        
        send(client, inp)

def init_client():
    global client
    if client == None:
        client = netcom.socket(ipv4, tcp)
    print(f'trying {IP}:{PORT}')
    try:
        client.connect((IP, PORT))
        print("connected, moving to shell..")
        client_shell(client)
    except Exception as e:
        print(f"error: {e}")
        print("lost connection to server.")
        exit()
        

def receive_file(client, path):
    data_received = 0
    part_size = 4096
    packet_size = client.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    print(f"Packet Size: {packet_size}")
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
    print(f"file downloaded\nfile written to path.\nData expected: {packet_size}\nData received: {data_received}")

def send(client, data):
    head = str(len(data)).zfill(header_size)
    data = head + data
    client.send(data.encode("utf-8"))

def receive(client):
    data_received = b''
    packet_size = client.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    while len(data_received) < packet_size:
        data_received += client.recv(packet_size - len(data_received))
    data_received = data_received.decode("utf-8")
    return data_received

init_client()
