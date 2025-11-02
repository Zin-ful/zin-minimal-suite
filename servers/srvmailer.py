from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import threading as task
port = 52311

server = netcom.socket(ipv4, tcp)

server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)

server.bind(("0.0.0.0", port))

home = "/opt/zinapp/mailboxes"

if "zinapp" not in os.listdir("/opt"):
    os.mkdir("/opt/zinapp")
if "mailboxes" not in os.listdir("/opt/zinapp"):
    os.mkdir(home)

server.listen(1)
print(f"listening on port {port}")
   

def init():
    while True:
        try:
            client, client_ip = server.accept()
            print(f"client accepted: {client_ip}")
            thread_client = task.Thread(target=client_start, args=[client, client_ip])
            thread_client.start()
        except Exception as e:
            print(e)
            
def client_start(client, client_ip):
    print("starting client")
    check = client.recv(3).decode("utf-8")
    if check:
        print("acked")
    while True:
        response = None
        try:
            exec = client.recv(10024).decode("utf-8")
            if not exec:
                client_end(client, client_ip)
                break
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            client_end(client, client_ip)
            break
        if exec:
            if " " not in exec:
                client.send("sorry, that isnt a command".encode("utf-8"))
                continue
            print(f"msg from {client_ip}")
            if "(!USER)" in exec:
                current_mailbox, exec = exec.split(" ", 1)
                current_mailbox = current_mailbox.strip("(!USER)")
                print("user found")
            else:
                current_mailbox = None
            
            if exec.strip() == "get mail":
                send_mail(client, current_mailbox)
                continue
            elif exec.strip() == "get box":
                send_box(client)
                continue
            exec, data = exec.split(" ", 1)
            print(exec)
            for name, func in cmd.items():
                if exec.strip() == name:
                    exec = cmd.get(name)
                    response = exec(current_mailbox, data)
                    break
            if not response:
                response = "Command not found."
            client.send(response.encode("utf-8"))

def client_end(client, client_ip):
    print(f"{client_ip} disconnected")
    client.close()
    print("client closed")

def remove_mail(box, name):
    if not box:
        return "you have to select a mailbox first"
    access_index = 0
    inbox = os.listdir(home+"/"+box)
    name = name+".txt"
    for item in os.listdir(home+"/"+box):
        if name in item:
            name = item
    if name not in inbox:
        try:
            name = int(name.strip(".txt"))
            access_index = 1
        except Exception as e:
            print(e)
            return "Mail with that name doesnt exist"
        if name > len(inbox) - 1 or name < 0:
            return "Mail with that index doesnt exist"
        else:
            name = inbox[name]            
    try:
        os.remove(home+"/"+box+"/"+name)
    except Exception as e:
        print(e)
        return "Error occured"
    return "file removed. no trash bin exists so...."

def send_mail(client, box):
    reply = ''
    if not box:
        client.send("you have to select a mailbox first".encode("utf-8"))
        return
    if box in os.listdir(home):
        for item in os.listdir(home+"/"+box):
            reply += item.strip(".txt")+'\n'
    else:
        reply = "User does not exist"

    if not reply:
        reply = "no mail"
    client.send(reply.encode("utf-8"))

def send_box(client):
    reply = ''
    for item in os.listdir(home):
        reply += item+'\n'
    if not reply:
        reply = "No boxes created"
    client.send(reply.encode("utf-8"))

def create(box, name):
    if name not in os.listdir(home):
        os.mkdir(home+"/"+name)
        return f"Mailbox {name} has been created!"
    else:
        return f"Mailbox {name} already exists"
def select_box(box, name):
    if name in os.listdir(home):
        return f"(!USER){name}"
    else:
        return "no mailboxes exist with that name"

def mail(box, name):
    name, title = name.split("/t/", 1)
    if name not in os.listdir(home):
        return f"Mailbox {name} does not exist."
    title, header = title.split("/h/", 1)
    header, body = header.split("/b/", 1)
    i = 0
    while header in os.listdir(home+"/"+name):
        if i > 1:
            header = header.strip(f"-{i-1}")
        header = header +f"-{i}"
    path = home+"/"+name+"/"+title
    with open(path+".txt", "w") as file:
        file.write(f"##{header}##\n")
        file.write(body)
    return "Mail sent!"

def view_mail(box, name):
    access_index = 0
    inbox = os.listdir(home+"/"+box)
    name = name+".txt"
    for item in os.listdir(home+"/"+box):
        if name in item:
            name = item
    if name not in inbox:
        try:
            name = int(name.strip(".txt"))
            access_index = 1
        except Exception as e:
            print(e)
            return "Mail with that name doesnt exist"
        if name > len(inbox) - 1 or name < 0:
            return "Mail with that index doesnt exist"
        else:
            name = inbox[name]
    try:
        with open(home+"/"+box+"/"+name, "r") as file:
            data = file.read()
            if not data:
                return "No data found in mail file. Contact server owner?"
            return data
    except Exception as e:
        print(e)
        return "Error occured"
cmd = {"remove": remove_mail, "open": view_mail, "select": select_box, "mail": mail, "create": create}

init()
