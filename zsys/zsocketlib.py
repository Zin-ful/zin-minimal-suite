from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
server = None
header_size = 100 #zfill
ACK = "ack"
def init(srv):
    global server
    server = srv

def receive_file(screens, path):
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

def send_file(screens, path):
    with open(path, "rb") as file:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
    head = file_size.zfill(header_size)
    server.send(str(head).encode("utf-8"))
    ack(0)
    with open(path, "rb") as file:
        i = 0
        while True:
            part = file.read(4096)
            if not part:
                break
            server.send(part)
            i += 1
    ack(0)
    return 1

def send(screens, data, encoded):
    is_flagged = "n"
    for key, val in flags.items():
        if val in data:
            is_flagged = "y"
    head = str(len(data + is_flagged)).zfill(header_size)
    data = head + is_flagged + data
    server.send(data.encode("utf-8"))
    ack(0)

def receive(screens, encoded):
    data_received = b''
    packet_size = server.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    is_flagged = server.recv(1).decode("utf-8")
    if is_flagged == "y":
        flag = server.recv(6).decode("utf-8").strip("||")
    else:
        flag = None
    while len(data_received) < packet_size:
        data_received += server.recv(packet_size - len(data_received))
    ack(1)
    data_received = data_received.decode("utf-8")
    return flag, data_received

def ack(state):
    if not state:
        ack_acpt = server.recv(3).decode("utf-8")
    else:
        server.send(ACK.encode('utf-8'))
