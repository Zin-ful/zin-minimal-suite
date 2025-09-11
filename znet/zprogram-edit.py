import zsocketlib as zock
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
import subprocess as proc
import time

port = 23512

server = netcom.socket(ipv4, tcp)

zock.init(server)

ip = input("IP? >>> ")
server.connect((ip, int(port)))

def client_start():
    while True:
        server.send("ack".encode("utf-8"))
        status = server.recv(1024).decode("utf-8")
        print(status)
        inp = input("What program would you like to open?\n>>> ")
        if "y" not in inp:
            return



client_start()

zock.init()

