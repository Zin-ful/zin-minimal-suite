from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import threading as task
import subprocess as proc
import time

port = 49652
server = netcom.socket(ipv4, tcp)
print("socket created")
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
print("set socket options")
server.bind(("0.0.0.0", port))
print(f"bound to {port}")

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
    ack = client.recv(3).decode("utf-8")
    print("acked")
    if ack.strip() != "ack":
        print("client is out of sync, exiting")
        return
    client.send("(Enter path to file)".encode("utf-8"))
    while True:
        try:
            cmd = client.recv(256).decode("utf-8")
            if cmd:
                response = extract_vars(cmd)
            else:
                continue
            if response:
                reply = convert(response)
                client.send(f"{reply}\nWould you like to edit any of these variables?".encode("utf-8"))
                prompt(client, response)
            else:
                client.send("Program not found.".encode("utf-8"))
        except Exception as e:
            print(e)
            client.close()
            break

def prompt(client):
    confirm = client.recv(128).decode("utf-8")
    if "y" not in confirm.lower():
        ss(client, "returning to main")
        return

    ss(client, "Select your line and change its value.")
    while True:
        new_val = client.recv(256).decode("utf-8")
        if " " not in new_val.strip():
            ss(client, "invalid format, [name or index] [value]")
        break
    return extract_val(new_val)    

def write_vars(path, is_int, name, val):
    return

def extract_val(string):
    is_int = 1
    name, value = string.split(" ", 1)
    try:
        name = int(name.strip())
    except:
        is_int = 0
        print("not int")
    return is_int, name, value

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
    return vars

def convert(vars):
    string = ""
    for val, item in vars.items():
        string += str(val) + item + "\n"
    return string

def ss(client, string):
    client.send(string.encode("utf-8"))

init()