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
storage_path = '/etc/zfile_srvr/storage'
root_usr = ""
root_psw = ""

admin_params = {"user": root_usr, "pass": root_psw}
flags = {"-dw": "#*$^||", "-dr": "^($#||", "-t": "#%&$||", "-l": "*@%#||", "-c": "!)$@||", "-mk": "(!%)||"}
cmd_list = ["browse", "get file list","download file","upload file", "make folder", "login","logout", "create", "promote","demote","games","msg", "server test", "client test", "config", "help","exit"]

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
if "storage" not in os.listdir("/etc/zfile_srvr"):
    os.makedirs("/etc/zfile_srvr/storage", exist_ok=True)
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
            print("flag found")
            for key, val in flags.items():
                if val.strip("||") == flag:
                    print(f"flag: {key}")
                    execute = exec_flag.get(key)
                    execute(client, data)
                    break
        else:
            execute = exec_phrase.get(data)
            if execute:
                result = execute(client, data)
                send(client, result, 0)
            else:
                send(client, "command not found. client or server out of date/sync?", 0)
        
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
    if not data:
        return
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
    print(packet_size)
    packet_size = int(packet_size)
    print(f"size of transmit is: {packet_size}")
    is_flagged = client.recv(1).decode("utf-8")
    print(is_flagged)
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
    print(f"data receive successful: {data_received}")
    return flag, data_received

def ack(client, state):
    if not state:
        print("receiving ack")
        ack_acpt = client.recv(3).decode("utf-8")
        print(f"acknowledged: {ack_acpt}")
    else:
        print("sending ack..")
        client.send("ack".encode('utf-8'))

def get_user(client):
    for key, value in clients.items():
        if client == key:
            return value
"""file operations"""

def write_tree(client):
    name = get_user(client)
    with open(tree_path, "w") as file:
        file.write(storage+name, '\n')
        recurse(storage+name, 1, file)

def recurse(path, depth, file):
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            file.write("    " * depth + entry + '\n')
            if os.path.isdir(entry_path):
                recurse(entry_path, depth+1, file)

def find_file(name):
    root_list = os.listdir(root)
    for folder in root_list:
        current_dir = os.listdir(f"{root}/{folder}")
        for file in current_dir:
            if name in file:
                return f"file found in {folder}"
    return "file not found"

def receive_file(client, data):
    name = get_user(client)
    path = storage_path+name+"/"+data
    print(f"writing file to path: {path}")
    part_size = 4096
    print(f"getting header")
    packet_size = client.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    print(f"file size: {packet_size}")
    ack(client, 1)
    with open(path, "wb") as file:
        data_received = 0
        while data_received < packet_size:
            data_remaining = packet_size - data_received
            print(f"data received: {data_received}")
            part = client.recv(min(part_size, data_remaining))
            if not part:
                break
            file.write(part)
            data_received += len(part)
    ack(client, 1)
    send(client, f"file uploaded to {name+'/'+data}", 0)

def send_file(client, path):
    with open(path, "rb") as file:
        file.seek(0, 2)
        file_size = file.tell()
    head = file_size.zfill(header_size)
    client.send(str(head).encode("utf-8"))
    ack(client, 0)
    with open(path, "rb") as file:
        i = 0
        while True:
            part = file.read(4096)
            if not part:
                break
            client.send(part)
            i += 1
    ack(client, 0)
    return 1

def user_exists(user):
    print(f"checking users for {user.strip('/')+'.conf'}")
    if user.strip("/")+".conf" in os.listdir(user_path):
        return 1
    else:
        return 0

def folder_exists(user):
    print(f"checking storage for {user.strip('/')}")
    if user.strip("/") in os.listdir(storage_path):
        return 1
    else:
        return 0

def create_directory(user):
    try:
        os.makedirs(storage_path + user)
        return 1
    except Exception as e:
        print(f"error creating user directory: {e}")
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


"""login/logout"""

def create(client, data):
    print("creating user..")
    name = save(data)
    print(f"user is {name}") 
    if not name:
        send(client, "error creating account, information reserved.", 0)
        return
    if not create_directory(name):
        remove(name)
        send(client, "error creating account, folder creation failure", 0)
        return 
    clients.update({client: name})
    unverified.remove(client)
    print("user created and verified")
    send(client, f"Welcome {name}, for information on usage select 'help'.", 0)

def login(client, data):
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

def change_directory(client, data):
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

def list_directory(client, data):
    name = get_user(client)
    path = storage_path+name
    files = ''
    total = len(os.listdir(path))
    if total == 0:
        send(client, "no files in directory", 0)
        return
    count = 0
    for i in os.listdir(path):
        count += 1
        if count < total:
            files += i + ', '
        elif count == total:
            files += i
    send(client, files, 0)

def make_directory(client, data):
    name = get_user(client)
    path = storage_path+name
    #when tracking current directory, append that here
    os.makedirs(path+data, exist_ok=True)
    send(client, f"folder created at {path + data}", 0)

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

exec_flag = {"-dr": send_file, "-dw": receive_file, "-t": test, "-l": login, "-c": create, "-mk": make_directory}
exec_phrase = {"get file list": list_directory}
server_init()
