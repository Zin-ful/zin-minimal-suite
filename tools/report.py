from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import time
from time import sleep

port = 23621

server = netcom.socket(ipv4, tcp)
ip = "localhost"
server.connect((ip, int(port)))

def client_start():
    server.send("ack".encode("utf-8"))
    while True:
        server.recv(3)
        sleep(10)
        server.send("ack".encode("utf-8"))
        sleep(10)

client_start()
