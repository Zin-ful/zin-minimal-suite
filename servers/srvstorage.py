from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import sys
import os
import time
import threading as task    
import subprocess

IP = 'localhost'
PORT = 25415
header_size = 100 #zfill
config_path = '/opt/zinapp/zfile_srvr'
user_path = '/opt/zinapp/zfile_srvr/users'
storage_path = '/opt/zinapp/zfile_srvr/storage'
root_usr = ""
root_psw = ""
root_name = ""
admin_params = {"name": root_name, "user": root_usr, "pass": root_psw}

#pulled from bottom for reference
#exec_flag = {"-sf": send_file, "-rf": receive_file, "-t": test, "-l": login, "-c": create, "-mk": make_directory, "-br": init_browse}
flags = {"-rf": "#*$^||", "-sf": "^($#||", "-t": "#%&$||", "-l": "*@%#||", "-c": "!)$@||", "-mk": "(!%)||", "-br": "*!&_||"}
cmd_list = ["browse", "get file list","download file","upload file", "make folder", "login","logout", "create", "promote","demote", "server test", "client test", "config", "help","exit"]

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

if "zinapp" not in os.listdir("/opt"):
    os.mkdir("/opt/zinapp")
if "zfile_srvr" not in os.listdir("/opt/zinapp"):
    os.makedirs("/opt/zinapp/zfile_srvr", exist_ok=True)
if "users" not in os.listdir("/opt/zinapp/zfile_srvr"):
    os.makedirs("/opt/zinapp/zfile_srvr/users", exist_ok=True)  
if "storage" not in os.listdir("/opt/zinapp/zfile_srvr"):
    os.makedirs("/opt/zinapp/zfile_srvr/storage", exist_ok=True)
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
            admin_params["name"] = "admin"
            admin_params["user"] = "admin"
            admin_params["pass"] = "root"
        with open(f"{user_path}/admin.conf", "w") as file:
            for key, val in admin_params.items():
                file.write(f"{key}:{val}\n")
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

"""client browsing"""

def init_browse(client, path):
    name = get_user(client) #client needs to send data first
    root_path = storage_path+name
    first = 1
    while True:
        print(first)
        if not first:
            flag, path = receive(client, 0)
        else:
            first = 0
            path = ""
            flag = None

        path = root_path + path
        if flag:
            print("flag found")
            for key, val in flags.items():
                if val.strip("||") == flag:
                    print(f"flag: {key}")
                    execute = exec_flag.get(key)
                    execute(client, path)
                    continue
        if path == "br":
            break
        files = get_directory(path)
        if not files:
            send(client, "#None", 0)
            continue
        send(client, files, 0)
        
def get_directory(path):
    data = "" 
    for dir in os.listdir(path):
        if "." not in dir:
            dir += "/"
        data += dir+"::"
    return data
    
def make_directory(client, path):
    name = get_user(client) #making dirs is not working, its creating them at root. remove the leading / or complete the file path properly
    print(f"making directory for {name}")
    root_path = name
    if path[0] != "/":
        root_path += "/"
    root_path += path
    os.makedirs(root_path, exist_ok=True)
    print("directory made")
    send(client, f"Direcotry made at {root_path}", 0)
    print("informed client")
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
    user_dict = {"name": name.strip("/"), "user": user, "pass": passw}
    with open(f'{user_path}{name}.conf', "r") as file:
        data = file.readlines()
        for item in data:
            key, val = item.split(":")
            print(f"checking {key} & {val} against {user_dict[key]}")
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
    print("login: "+data)
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

exec_flag = {"-br": init_browse, "-sf": send_file, "-rf": receive_file, "-t": test, "-l": login, "-c": create, "-mk": make_directory}
server_init()
