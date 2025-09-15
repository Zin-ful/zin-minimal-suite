from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import time
import random
import threading

port = 19603

users = {}
user_list = []
user_path = "/etc/gamespack/"



waitout = 20

port = 39562
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
    client.send("1. login\n2.create\n".encode("utf-8"))
    while True:
        try:
            cmd = client.recv(256).decode("utf-8")
            if client not in user_list:
                if not init_account(cmd, client):
                    continue

            client.send(response.encode("utf-8"))
        except Exception as e:
            print(e)
            client.close()
            break


"""login/logout"""

def init_account(mode, client):
    while True:
        if "1" or "l" in mode.lower():
            client.send("(login)\nFormat: name user password".encode("utf-8"))
            info = client.recv(256).decode("utf-8")
            if "exit" in info:
                return 0
            if not info:
                client.send("(login)\nLogin failed. Either try again or type 'exit' to restart".encode("utf-8"))
                continue
            else:
                info = info.strip()
            if check_format(info. " ", 2):
                if login(client, data):
                    client.send("(login)\nYou have been logged in".encode("utf-8"))
                    break
                else:
                    client.send("(login)\nLogin failed. Either try again or type 'exit' to restart".encode("utf-8"))


    else:
        client.send("(create)\nFormat: name user password".encode("utf-8"))
        info = client.recv(256).decode("utf-8")
        if not info:
            return
        else:
            info = info.strip()
        if check_format(info. " ", 2):
            if create(client, data):
                client.send("(create)\nYour account has been created and you have been logged in".encode("utf-8"))
            else:
                client.send("(create)\nCreation failed. Either try again or type 'exit' to restart".encode("utf-8"))


def check_format(info, delim, expected_delim):
    i = 0
    for item in info:
        if item == delim:
            i += 1
    if i == expected_delim:
        return 1
    else:
        return 0


def remove(name):
    if user_exists(name):
        print(f"removing config of {name}")
        os.remove(user_path+name+".conf")
    if folder_exists(name):
        print(f"removing folder of {name}")
        os.rmdir(storage_path+name)
    return 1
    
def load(data):
    name, user, passw = data.split(' ')
    if name+".conf" not in os.listdir((user_path))
    user_dict = {"name": name, "user": user, "pass": passw}
    with open(f'{user_path}{name}.conf', "r") as file:
        data = file.readlines()
        for item in data:
            key, val = item.split(":")
            if user_dict[key] == val.strip('\n'):
                pass
            else:
                return 0
    return name
    
def save(data):
    name, user, passw = data.split(' ')
    if user_exists(name):
        return 0
    user_dict = {"name": name, "user": user, "pass": passw}
    with open(f'{user_path}{name}.conf', "w") as file:
        for key, val in user_dict.items():
            file.write(f"{key}:{val}\n")
    return name


def create(client, data):
    print("creating user..")
    name = save(data)
    print(f"user is {name}") 
    if not name:
        return 0
    if not create_directory(name):
        remove(name)
        return 0
    clients.update({client: name})
    print("user created and verified")
    return 1

def login(client, data):
    name = load(data)
    if not name:
        return 0
    clients.update({client: name})
    return 1

def logout():
    return
