from socket import SOCK_STREAM as tcp
from socket import AF_INET as ipv4
import socket as netcom
import threading as task
import datetime
import os
conf_path = "/opt/zinapp/ztext_srvr"
port = 34983
ip = "0.0.0.0"
passwd = "admin"
linky = "none"
contact = "none"

attr_dict = {"contact": contact, "link": linky, "passwd": passwd}

if not "zinapp" in os.listdir("/opt"):
    os.mkdir("/opt/zinapp")

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

def messenger(client_socket, addr):
    addr_id = str(addr)
    user_id, user_ip = addr_id.split(",")
    user_ip = user_ip.strip("(").strip("'").strip(")")
    user_id = user_ip.strip("(").strip("'").strip(")")

    username = client_socket.recv(128)
    if username:
        users_name.update({str(user_id): username.decode("utf-8")})
        #print("user sent")

    #print(f"user connected: {addr}")
    with clients_lock:
        users.append(client_socket)
    startmsg = f"server.message.from.server.users: {len(users)} !###########\nSYSTEM MESSAGE: user connected: {addr}\n###########"
    for other_client in users:
        if other_client != client_socket:
            try:
                other_client.sendall(startmsg.encode("utf-8"))
            except Exception as e:
                pass
    try:
        while True:
            msg = client_socket.recv(2048)
            if not msg:
                break
            message = f"{msg.decode('utf-8')}\n"
            if "server.main." in message and '"' not in message:
                cmd = message.replace("server.main.", "")
                log(client_socket, cmd)
                xcute = commands.get(cmd.strip())
                if xcute:
                     message = xcute(client_socket, message)
                else:
                    message = "server.message.from.server.invalid"
                log(client_socket, message)
                client_socket.sendall(message.encode("utf-8"))
                continue
            else:
                message = f"\n@{users_name.get(user_id)}: {msg.decode('utf-8')}\n"
            if len(users) <= 1:
                with open(f"{conf_path}/missed.txt", "a") as file:
                    file.write(f"{message}\n")
            #print(message)        
            with clients_lock:
                for other_client in users:
                    if other_client != client_socket:
                        try:
                            other_client.sendall(message.encode("utf-8"))
                        except Exception as e:
                            pass
                            #print(f"message send failed: {e}")
    except Exception as e:
        pass
        #print(f"message recv failed: {e}")
    finally:
        try:
            for user in users:
                user.sendall(f"server.message.from.server.users: -1 !###########\nSYSTEM MESSAGE: user DISconnected: {addr}\n###########".encode("utf-8"))
        except BrokenPipeError:
            pass
        with clients_lock:
            users.remove(client_socket)
        client_socket.close()


load()
while True:
    try:
        server.listen(10)
        #print(f"server listening on ip: {ip} and port {port}")
        client_socket, addr = server.accept()
        client_thread = task.Thread(target=messenger, args=(client_socket, addr))
        client_thread.start()
    except Exception as e:
        pass
        #print(f"threading failed: {e}")
