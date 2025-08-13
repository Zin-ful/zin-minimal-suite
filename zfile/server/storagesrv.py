from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import sys
import os
import time
import threading as task    
import subprocess

IP = 'localhost'
PORT = 12345
header_size = 100 #zfill
config_path = '/etc/zfile_srvr'
user_path = '/etc/zfile_srvr/users'
root_usr = ""
root_psw = ""

admin_params = {"user": root_usr, "pass": root_psw}
flags = {"-dw": ")#*$^||", "-dr": "^($#||", "-t": "#%&$||", "-l": "*@%#||", "-c": "!)$@||"}
white_list = [flags["-c"].strip("||"), flags["-l"].strip("||")]
unverified = []
clients = {}
recv_cmd = b''
logged_in = False
status = None

client_conn = netcom.socket(ipv4, tcp) #creates and defines sock obj
client_conn.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
client_conn.bind((IP,  PORT)) #temp

"""first time server setup"""

if "zfile_srvr" not in os.listdir("/etc"):
    os.makedirs("/etc/zfile_srvr", exist_ok=True)
if "users" not in os.listdir("/etc/zfile_srvr"):
    os.makedirs("/etc/zfile_srvr/users", exist_ok=True)  
if "admin.conf" in os.listdir(user_path):
    print("admin exists")
else:
    while True:
        server_ask = input("admin files are not detected. would you like to set the username and password?\n(selecting not to will set the default to admin and root, the default name is always /admin)\n>>> ")
        if "y" in server_ask:
            root_usr = input("username?\n>>> ")
            root_psw = input("password?\n>>> ")
            server_ask = input(f"you entered {root_usr} and {root_psw}\nare you sure you want to make these changes?\n>>> ")
            if "y" in server_ask:
                pass
            else:
                continue
        else:
            root_usr = "admin"
            root_psw = "root"
        with open(f"{user_path}/admin.conf", "w") as file:
            for name, item in admin_params.items():
                file.write(f"{name}={item}")
        break

"""main client"""
def client_start(client):
    while True:
        flag, data = receive(client, 0)
        if client in unverified:
            print(f"client not verified, attempted flag: {flag}")
            if str(flag) not in white_list:
                send(client, "You need to login before executing commands.", 0)
                continue
        print("flag is in whitelist. continuing")
        if flag:
            for key, val in flags.items():
                if val.strip("||") == flag:
                    execute = exec_flag.get(key)
                    execute(client, data)
                    break
            continue
        
"""helper functions"""
def test(client, data):
    for i in range(9):
        send(client, flags["-t"]+f"Echoing packet: {i}", 0)
        response = receive(client, 0)
        print(response)
    if get_response(client, "Basic echo test pass, would you like to continue?", "y"):
        pass
    else:
        return

def get_response(client, message, delimiter):
    send(client, message, 0)
    response = receive(client, 0)
    if delimiter in response:
        return 1
    else:
        return 0

def send(client, data, encoded):
    is_flagged = "n"
    for key, val in flags.items():
        if val in data:
            is_flagged = "y"
    print(f"sending data: {data}\nsize of data is {len(data + str(header_size))}")
    head = str(len(data)).zfill(header_size)
    data = head + is_flagged + data
    client.send(data.encode("utf-8"))
    print("data sent")
    ack(client, 0)

def receive(client, encoded):
    print("receiving header..")
    data_received = b''
    packet_size = client.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    print(f"size of transmit is: {packet_size}")
    is_flagged = client.recv(1).decode("utf-8")
    packet_size -= 1
    if is_flagged == "y":
        print("is flagged")
        flag = client.recv(6).decode("utf-8").strip("||")
        packet_size -= 6
        print(f"flag: {flag}")
    else:
        print("is not flagged")
        flag = None
    print("receiving data..")
    while len(data_received) < packet_size:
        data_received += client.recv(packet_size - len(data_received))
        print(f"data being received: {packet_size} | {len(data_received)}")
    ack(client, 1)
    data_received = data_received.decode("utf-8")
    print("data receive successful")
    return flag, data_received

def ack(client, state):
    if not state:
        print("receiving ack")
        ack_acpt = client.recv(3).decode("utf-8")
        print("acknowledged")
    else:
        print("sending ack..")
        client.send("ack".encode('utf-8'))

"""file operations"""

def send_file(client, path, encoded):
    return

def receive_file(client, path, encoded):
    return

def user_exists(user, path):
    if user in os.listdir(path):
        return 1
    else:
        return 0

def load(data):
    name, user, passw = data.split(' ')
    user_dict = {"name": name, "user": user, "pass": passw}
    with open(f'{user_path}{name}.conf', "r") as file:
        data = file.readlines()
        for item in data:
            key, val = item.split()
            if user_dict[key] == val.strip['\n']:
                pass
            else:
                return 0
    return name
    
def save(data):
    name, user, passw = data.split(' ')
    user_dict = {"name": name, "user": user, "pass": passw}
    if user_exists(user_path, name):
        return 0
    with open(f'{user_path}{name}.conf', "w") as file:
        for key, val in user_dict.items():
            file.write(f"{key}:{val}\n")
    return name


"""login/logout"""

def create(client, data):
    flag, data = receive(client, 0)
    name = save(data)
    if not name:
        send(client, "login credentials invald.", 0)
        return
    clients.update({client: name})
    unverified.remove(client)
    send(client, f"Welcome {name}, for information on usage select 'help'.", 0)

def login(client, data):
    flag, data = receive(client, 0)
    name = load(data)
    if not name:
        send(client, "login credentials invald.", 0)
        return
    clients.update({client: name})
    unverified.remove(client)
    send(client, f"Welcome {name}, access to functions restored.", 0)
    
    



def logout():
    return

"""user functions"""

def change_directory(name):
    white_list = [user, "home","root","back",".."]
    if name not in os.listdir(path) and name not in white_list:
        return "that directory does not exist"
    elif "." in name:
        return "cannot move into a file"
    if not any('/' in d for d in name):
        name = '/' + name
    if name in white_list:
        path = root
        return f'directory changed to {path}'
    elif not '/storage' in name:
        path = path + str(name)
        return f'directory changed to {path}'
    else:
        return 'directory not found, might not exist'

def list_directory():
    files = ''
    total = len(os.listdir(path))
    count = 0
    for i in os.listdir(path):
        count += 1
        if count < total:
            files += i + ', '
        elif count == total:
            files += i
    return files

def find_file(name):
    root_list = os.listdir(root)
    for folder in root_list:
        current_dir = os.listdir(f"{root}/{folder}")
        for file in current_dir:
            if name in file:
                return f"file found in {folder}"
    return "file not found"

def server_init():
    while True:
        try:
            print(f"listening on {IP}:{PORT}")
            client_conn.listen()
            client, client_ip = client_conn.accept()
            print(f"client accepted and is not verified\n{client}\n{client_ip}")
            unverified.append(client)
            ack(client, 0)
            thread_client = task.Thread(target=client_start, args=[client]) #comma cause args are tuples
            thread_client.start()
        except Exception as e:
            print(e)

exec_flag = {"-dw": send_file, "-dr": receive_file, "-t": test, "-l": login, "-c": create}

server_init()
