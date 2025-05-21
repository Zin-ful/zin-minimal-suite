from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import sys
import json
import os
import time
import threading as task
import handle_cmd
from handle_cmd import send_in_chunk
import subprocess

IP = 'localhost'
PORT = 12345
header_size = 100 #zfill
config_path = '/etc/zfile_srvr'
user_path = '/etc/zfile_srvr/users'
ack = 'ACK'
recv_cmd = b''
logged_in = False
status = None
client_conn = netcom.socket(ipv4, tcp) #creates and defines sock obj
client_conn.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
client_conn.bind((IP,  PORT)) #temp

check_admin = os.listdir(user_path)
if "admin.json" in check_admin:
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
        with open(f"{user_path}/admin.json", "w") as file:
            data = {"/admin": {"user": root_usr, "password": root_psw, "priv": "1"}}
            json.dump(data, file)
        break


#check for OS version
def get_software():
    return

def do_connect():
    while True:
        try:
            client_conn.listen()
            curr_client, client_ip = client_conn.accept()
            print(f"client accepted,\n{curr_client}\n{client_ip}")
            thread_client = task.Thread(target=client_cmd, args=(curr_client,)) #comma cause args are tuples
            thread_client.start()
        except Exception as e:
            print(e)

def client_cmd(conn):
    global cmd_dict
    cmd_dict = {
        "login":login,
        "help":help,
        "exit":xit
        }
    while True:
        recv_cmd = b''
        pck_sze = 0
        ack_acpt = b''
        try:
            ack_acpt = conn.recv(3).decode("utf-8")
            print(ack_acpt)
            pck_sze = conn.recv(header_size).decode("utf-8")
            if pck_sze == '' or pck_sze == ' ' or pck_sze == None:
                conn.send(ack.encode('utf-8'))
                continue
            print(pck_sze)
            pck_sze = int(pck_sze)
            if pck_sze > 4096:
                while True:
                    chunk = conn.recv(4096)
                    recv_cmd += chunk
                    if recv_cmd >= chunk:
                        thread_client = task.Thread(target=send_in_chunk, args=(recv_cmd,)) #comma cause args are tuples
                        thread_client.start()
                    else:
                        send_in_chunk(recv_cmd)
                        conn.send(ack.encode('utf-8'))
                        continue
            else:
                while len(recv_cmd) < pck_sze:
                    recv_cmd += conn.recv(pck_sze - len(recv_cmd))
            conn.send(ack.encode('utf-8'))
            recv_cmd = recv_cmd.decode("utf-8")
            print(recv_cmd)
        except:
            logout()
        if "|" in recv_cmd:
            xcute = cmd_dict.get(recv_cmd.strip("|"))
            if xcute:
                data = xcute(conn) #for games, data will have to return and be sent to client or else the server will fail due to lack of ack
            else:
                if logged_in == True:
                    data = "Invalid command"
                else:
                    data = "You are not logged in."
        elif ' ' in recv_cmd and logged_in == True:
            print(recv_cmd)
            cmd, cmd2 = recv_cmd.split(' ', 1)
            data = handle_cmd.command(status, cmd, cmd2)

        elif logged_in == True:
            cmd2 = ''
            data = handle_cmd.command(status, recv_cmd, *cmd2)
        else:
            data = "You are not logged in."
        if data == "sent":
            continue
        head = str(len(data)).zfill(header_size)
        data = head + data
        conn.send(data.encode("utf-8"))

def login(conn):
    try:
        recv_cmd = b''
        prompt = "please login. format:\n/name username password"
        head = str(len(prompt)).zfill(header_size)
        data = head + prompt
        conn.send(data.encode("utf-8"))
        ack_acpt = conn.recv(3).decode("utf-8")
        print(ack_acpt)
        pck_sze = conn.recv(header_size).decode("utf-8")
        pck_sze = int(pck_sze)
        while len(recv_cmd) < pck_sze:
            recv_cmd += conn.recv(pck_sze - len(recv_cmd))
        conn.send(ack.encode('utf-8'))
        recv_cmd = recv_cmd.decode("utf-8")
        name, user, passw = recv_cmd.split(' ')
        try:
            with open(f"{user_path}{name}.json", 'r') as file:
                load = json.load(file)
                load_user = load[f"{name}"]["user"]
                load_passw = load[f"{name}"]["password"]
                global status
                status = load[f"{name}"]["priv"]
        except Exception as e:
            if e:
                print(e)
            result = "invalid information"
            return result
        if user == load_user and passw == load_passw:
            global logged_in 
            logged_in = True
            handle_cmd.pass_user(str(name))
        else:
            return 'login creds invalid'
        result = f"logged in successfully, welcome {name.strip('/')}"
    except Exception as e:
        result = f"login failed due do to:\n{e}"
    login_check()
    return result

def logout(conn):
    global cmd_dict, logged_in, status
    cmd_dict = {
        "login":login,
        "help":help,
        "exit":xit
        }
    logged_in = False
    status = None
    print("user has logged out")
    logout_msg = "logged out"
    header = str(len("logged out")).zfill(header_size)
    data = header + logout_msg
    conn.send(data.encode("utf-8"))
    time.sleep(3)
    conn.close()
    time.sleep(2)
    do_connect()
def create(conn):
    try:
        recv_cmd = b''
        prompt = f"create user & password. format:\n/name username password"
        head = str(len(prompt)).zfill(header_size)
        data = head + prompt
        conn.send(data.encode("utf-8"))
        ack_acpt = conn.recv(3).decode("utf-8")
        pck_sze = conn.recv(header_size).decode("utf-8")
        pck_sze = int(pck_sze)
        while len(recv_cmd) < pck_sze:
            recv_cmd += conn.recv(pck_sze - len(recv_cmd))
        conn.send(ack.encode('utf-8'))
        recv_cmd = recv_cmd.decode("utf-8")
        try:
            name, user, passw = recv_cmd.split(' ')
        except Exception as e:
            print(e)
        with open(f'{user_path}{name}.json', "w") as file:
            data = {name: {"user":user, "password":passw, "priv":"0"}}
            json.dump(data, file)
        subprocess.run(["mkdir", f"storage/{name}"])
        result = "account created successfully"
    except Exception as e:
        result = f"account creation failed due do to:\n{e}"
    return result

def makeadmin(conn):
    try:
        recv_cmd = b''
        info = f"what user do you want to promote to admin?"
        head = str(len(prompt)).zfill(header_size)
        data = head + prompt
        conn.send(data.encode("utf-8"))
        ack_acpt = conn.recv(3).decode("utf-8")
        print(ack_acpt)
        pck_sze = conn.recv(header_size).decode("utf-8")
        pck_sze = int(pck_sze)
        while len(recv_cmd) < pck_sze:
            recv_cmd += conn.recv(pck_sze - len(recv_cmd))
        conn.send(ack.encode('utf-8'))
        user = recv_cmd.decode("utf-8")
        try:
            with open(f"{user_path}{name}.json", 'r') as file:
                load = json.load(file)
                load_user = load[f"{name}"]["user"]
                load_passw = load[f"{name}"]["password"]
                load_status = load[f"{name}"]["priv"]
            with open(f"{user_path}{name}.json", 'w') as file:
                data = {name: {"user":load_user, "password":load_passw, "priv":"1"}}
                json.dump(data, file)
        except Exception as e:
            if e:
                print(e)
            print('creds invalid')
    except Exception as e:
        print(e)
    result = f"{load_user} has been promoted to admin."
    return result

def removeadmin(conn):
    try:
        recv_cmd = b''
        info = f"what user do you want to demote?"
        head = str(len(prompt)).zfill(header_size)
        data = head + prompt
        conn.send(data.encode("utf-8"))
        ack_acpt = conn.recv(3).decode("utf-8")
        print(ack_acpt)
        pck_sze = conn.recv(header_size).decode("utf-8")
        pck_sze = int(pck_sze)
        while len(recv_cmd) < pck_sze:
            recv_cmd += conn.recv(pck_sze - len(recv_cmd))
        conn.send(ack.encode('utf-8'))
        user = recv_cmd.decode("utf-8")
        try:
            with open(f"{user_path}{name}.json", 'r') as file:
                load = json.load(file)
                load_user = load[f"{name}"]["user"]
                load_passw = load[f"{name}"]["password"]
                load_status = load[f"{name}"]["priv"]
            with open(f"{user_path}{name}.json", 'w') as file:
                data = {name: {"user":load_user, "password":load_passw, "priv":"0"}}
                json.dump(data, file)
        except Exception as e:
            if e:
                print(e)
            print('creds invalid')
    except Exception as e:
        print(e)
    result = f"{load_user} has been demoted." #load_user here so we dont have to use an extra function (strip)
    return result

def config(conn):
    return
def xit(conn):
    return
def msg(conn):
    return
def message(conn):
    print("opening client..")
def games(conn):
    game_dict = {"freeland":"freeland.game(conn)", "battle tower":"btower.game(conn)", "dice roller":"roller.main(conn)"} #adjust for actual function names and pass conn
    game_list = ["Freeland", "Battle Tower", "Dice Roller"]
    for i in game_list:
        print(i)
    client_ask = input("what program would you like to run?\n>>> ")
    xcute = game_dict.get(client_ask)
    if xcute:
        xcute(conn) #will have to complete client ack/datarecv cycle so the module can take over
def help(conn):
    res = ''
    for i in cmd_dict.keys():
        res += i + "\n"
    if logged_in == True:
        res += "send\nget\nremove\nupdate\nprint\nlist\nmakefd\nchange\ninfo\npwd\nhelp\n"
        if status == "1":
            res += "compress\nproperties\nsystem\npriv\nsys-help\n"
    return f"commands:\n{res}"
def login_check():
    if logged_in == True:
        if status == "1":
            cmd_dict.update({"logout": logout, "create":create, "config":config, "promote":makeadmin, "msg":message, "games":games})
        else:
            cmd_dict.update({"msg":msg, "games":games, "logout": logout})
print(f"listening on {IP}:{PORT}")
do_connect()
