from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import time
import random
import threading

port = 19603

server = netcom.socket(ipv4, tcp)

zock.init(server)
ip = input("IP? >>> ")
server.connect((ip, int(port)))

def client_start():
    server.send("ack".encode("utf-8"))
    while True:
        response = server.recv(1024).decode("utf-8")
        reply = input(f"{response}\n>>> ")
        server.send(reply.encode("utf-8"))



client_start()