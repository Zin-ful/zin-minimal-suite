from socket import SOCK_STREAM as tcp
from socket import AF_INET as ipv4
import socket as netcom
import threading as task
import datetime
import os

"""
FIX

In direct message, make sure the direct messanger doesnt recieve group chat texts
In direct message, make sure users dont see the system connected message
Test missed message sending
"""

conf_path = "/opt/zinapp/ztext_srvr"
port = 34983
ip = "0.0.0.0"
passwd = "admin"
linky = "none"
contact = "none"

missed_path = "/opt/zinapp/ztext/missed/" 

attr_dict = {"contact": contact, "link": linky, "passwd": passwd}

if not "zinapp" in os.listdir("/opt"):
    os.mkdir("/opt/zinapp")

if not "ztext" in os.listdir("/opt/zinapp"):
    os.mkdir("/opt/zinapp/ztext")

if not "missed" in os.listdir("/opt/zinapp/ztext"):
    os.mkdir("/opt/zinapp/ztext/missed")

def load():
    try:
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for line in file.readlines():
                name, val = line.split("=", 1)
                attr_dict[name.strip()] = val.strip()
    except Exception as e:
        #print(e)
        os.makedirs(conf_path, exist_ok=True)
        with open(f"{conf_path}/msg_server.conf", "a") as file:
            for name, val in attr_dict.items():
                file.write(f"{name} = {val}\n")
        #print("generating report file")
        with open(f"{conf_path}/reports.txt", "w") as file:
            file.write("")
        with open(f"{conf_path}/missed.txt", "w") as file:
            #print("generating missed messages file")
            file.write("")

server = netcom.socket(ipv4, tcp)
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
server.bind((ip, port))



users = []
users_name = {}
clients_lock = task.Lock()

def contact(client_socket, msg):
    return f"server.message.from.server.{attr_dict['contact']}"

def link(client_socket, msg):
    return f"server.message.from.server.{attr_dict['link']}"

def helpy(client_socket, msg):
    return "server.message.from.server.bug-report\nlist-users\nget-link\nget-contact\nset-link\nset-contact\nset-password\nhelp"

def bug_report(client_socket, msg):
    client_socket.send("server.message.from.server.Please submit the issue you encountered and the steps to reproduce (if any)".encode("utf-8"))
    bug = client_socket.recv(1024)
    if bug:
        bug = bug.decode("utf-8")
        with open(f"{conf_path}/reports.txt", "a") as file:
            file.write(f"{datetime.datetime.now()} report: {bug}\n")
        return "server.message.from.server.Submitted!"
    else:
        return "server.message.from.server.you cant exactly submit a bug without the.. yknow.. bug?"

def list_users(client_socket, msg):
    if msg:
        msg = ""
        for i in users_name.values():
            msg += f"{i}\n"
        return f"server.message.from.server. {msg}"

def updlink(client_socket, msg):
    client_socket.send("server.message.from.server.Updating link. Submit your response in this format: {password}:{link}".encode("utf-8"))
    response = client_socket.recv(1024)
    if response:
        response = response.decode("utf-8")
        try:
            auth, link = response.split(":", 1)
        except:
            return "server.message.from.server.improper format, maybe forgot the ':' ?"
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for item in file.readlines():
                if "passwd" in item:
                    trash, passwd = item.split("=", 1)
        if passwd.strip() == auth.strip():
            attr_dict["link"] = link
            with open(f"{conf_path}/msg_server.conf", "w") as file:
                file.write("")
            with open(f"{conf_path}/msg_server.conf", "a") as file:
                for name, val in attr_dict.items():
                    file.write(f"{name} = {val}\n")
        else:
            return "server.message.from.server.invalid password"
    else:
        return "server.message.from.server.you know you have to say something, right?"
    return "server.message.from.server.link updated"

def updcontact(client_socket, msg):
    client_socket.send("server.message.from.server.Updating contact information. Submit your response in this format: {password}:{contact}".encode("utf-8"))
    response = client_socket.recv(1024)
    if response:
        response = response.decode("utf-8")
        try:
            auth, cont = response.split(":", 1)
        except:
            return "server.message.from.server.improper format, maybe forgot the ':' ?"
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for item in file.readlines():
                if "passwd" in item:
                    trash, passwd = item.split("=", 1)
        if passwd.strip() == auth.strip():
            attr_dict["contact"] = cont
            with open(f"{conf_path}/msg_server.conf", "w") as file:
                file.write("")
            with open(f"{conf_path}/msg_server.conf", "a") as file:
                for name, val in attr_dict.items():
                    file.write(f"{name} = {val}\n")
        else:
            return "server.message.from.server.invalid password"
    else:
        return "server.message.from.server.you cant just say nothing"
    return "server.message.from.server.contact updated"

def updpasswd(client_socket, msg):
    client_socket.send("server.message.from.server.Updating admin password. Submit your response in this format: {oldpass}:{newpass}".encode("utf-8"))
    response = client_socket.recv(1024)
    if response:
        response = response.decode("utf-8")
        try:
            old, new = response.split(":", 1)
        except:
            return "server.message.from.server.improper format, maybe forgot the ':' ?"
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            for item in file.readlines():
                if "passwd" in item:
                    trash, passwd = item.split("=", 1)
        if old.strip() == passwd.strip():
            attr_dict["passwd"] = new
            with open(f"{conf_path}/msg_server.conf", "w") as file:
                file.write("")
            with open(f"{conf_path}/msg_server.conf", "a") as file:
                for name, val in attr_dict.items():
                    file.write(f"{name} = {val}\n")
        else:
            return "server.message.from.server.old password is invalid"
    else:
        return "server.message.from.server.not one for words, are ya?"

    return "server.message.from.server.password updated"

commands = {"bug-report":bug_report,"get-users": list_users,"get-link": link, "get-contact": contact, "help":helpy, "set-link": updlink, "set-contact": updcontact, "set-password": updpasswd}

def log(client_socket, msg):
    if msg:
        with open(f"{conf_path}/log.txt", "a") as file:
            file.write(f"from {client_socket}: {msg}\n")

def send_message(client, msg):
    try:
        client.sendall(msg.encode("utf-8"))
        return 1
    except (BrokenPipeError, ConnectionResetError):
        client_end(client)
        return 0

def receive_message(client):
    try:
        msg = client.recv(2048)
        if msg:
            return msg
        else:
            client_end(client)
            return 0
    except (BrokenPipeError, ConnectionResetError):
        client_end(client)
        return 0

def save_missed(name, message):
    with open(missed_path+f"{name}.txt", "a") as file:
        file.write(message+"\n")

def check_missed(name):
    missed = None
    if f"{name}.txt" not in missed_path:
        return None
    with open(missed_path+f"{name}.txt", "r") as file:
        check = file.readlines()
        while True:
            if len(check) < 15:
                for item in check:
                    missed += item
            else:
                i = 0
                while i < 10:
                    check.pop(i)
                    i += 1
    if missed:
        return missed
    else:
        return None

def direct_send(message, source_user):
    try:
        username, message = message.split(":", 1)
    except:
        return
    username = username.strip("@")
    for id, user in users_name.items():
        if username.lower().strip() == user.lower().strip():
            send_message(id, f"\n@{source_user}: {message}\n")
            break
    save_missed(username, message)
            
def messenger(client_socket, addr):
    addr_id = str(addr)
    user_id, user_ip = addr_id.split(",")
    user_ip = user_ip.strip("(").strip("'").strip(")")
    user_id = user_ip.strip("(").strip("'").strip(")")

    username = client_socket.recv(128)
    if username:
        users_name.update({client_socket: username.decode("utf-8")})

    print(f"user connected: {addr}")
    with clients_lock:
        users.append(client_socket)
    startmsg = f"server.message.from.server.users: {len(users)} !###########\nSYSTEM MESSAGE: user connected: {addr}\n###########"
    for other_client in users:
        if other_client != client_socket:
            if not send_message(other_client, startmsg):
                break
    missed = check_missed(username)
    if missed:
        client.send("SYSTEM MISSED MESSAGES\n{missed}")
    while True:
        msg = receive_message(client_socket)
        if not msg:
            break
        message = f"{msg.decode('utf-8')}\n"
        if message[0] == "@":
            direct_send(message, users_name.get(user_id))
            continue
        if "server.main." in message and '"' not in message:
            cmd = message.replace("server.main.", "")
            log(client_socket, cmd)
            xcute = commands.get(cmd.strip())
            if xcute:
                message = xcute(client_socket, message)
            else:
                message = "server.message.from.server.invalid"
            log(client_socket, message)
            if not send_message(client_socket, message):
                break
            continue
        else:
            message = f"\n@{users_name.get(user_id)}: {msg.decode('utf-8')}\n"
        if len(users) <= 1:
            with open(f"{conf_path}/missed.txt", "a") as file:
                file.write(f"{message}\n")
        with clients_lock:
            for other_client in users:
                if other_client != client_socket:
                    if not send_message(other_client, message):
                        break
        
def client_end(client):
    print("ending client")
    try:
        for user in users:
            user.sendall(f"server.message.from.server.users: -1 !###########\nSYSTEM MESSAGE: user DISconnected: {addr}\n###########".encode("utf-8"))
    except BrokenPipeError:
        pass
    with clients_lock:
        users.remove(client)
    client.close()
    print("client disconnected")


load()
server.listen(10)
print(f"server listening on ip: {ip} and port {port}")
        
while True:
    try:
        client_socket, addr = server.accept()
        client_thread = task.Thread(target=messenger, args=(client_socket, addr))
        client_thread.start()
    except Exception as e:
        pass
