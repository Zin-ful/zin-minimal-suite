from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import time


port = 23512

server = netcom.socket(ipv4, tcp)
ip = input("IP? >>> ")
server.connect((ip, int(port)))

def client_start():
    while True:
        server.send("ack".encode("utf-8"))
        status = server.recv(1024).decode("utf-8")
        print(status)
        inp = input("Check again?\n>>> ")
        if "y" not in inp:
            return



client_start()
