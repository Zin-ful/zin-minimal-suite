from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import time
from time import sleep

port = 52311

user = None

server = netcom.socket(ipv4, tcp)

ip = input("IP address? >>> ")

if not ip:
    ip = "localhost"

server.connect((ip, int(port)))

autofill = {"gm": "get mail", "gb": "get box", "m": "mail", "o": "open",
 "s": "select", "c": "create", "sel": "select", "ma": "mail", "op": "open",
 "cr": "create", "r": "remove", "rm": "remove", "rem": "remove"}

def client_start():
    global user
    server.send("ack".encode("utf-8"))
    print("Connected to server!\nType 'help' for a list of commands")
    while True:
        inp = input(f"{user} | (shell) >>> ")
        for item, fill in autofill.items():
            cache = None
            if " " in inp:
                inp, cache = inp.split(" ", 1)
            if inp.strip() == item:
                inp = autofill.get(item)
            if cache:
                inp += " "+cache
                
        if inp == "mail":
            inp = mail()
            if not inp:
                continue
        if inp == "help":
            for item, desc in cmds.items():
                print(f"{item}: {desc}")
            continue
        else:
            if user:
                server.send(f"(!USER){user} {inp}".encode("utf-8"))
            else:
                server.send(inp.encode("utf-8"))
            response = server.recv(4096).decode("utf-8")
            if response:
                if "(!USER)" in response:
                    user = response.strip("(!USER)")
                else:
                    print(response)

def mail():
    body = []
    print("MAKE SURE USER ACTUALLY EXISTS")
    name = input("(/q/ to exit) Mail To: ")
    if not name:
        print("name required")
        return 0
    elif name == "/q/":
        return 0
    title = input("(/q/ to exit) Title: ")
    if not title:
        title = "No Title"
    elif title == "/q/":
        return 0
    title = f"from {user}: {title}"
    subject = input("(/q/ to exit) Subject: ")
    if not subject:
        subject = "No Subject"
    elif subject == "/q/":
        return 0
    message = name+"/t/"+title+"/h/"+subject+"/b/"
    i = 0
    while True:
        line = input(f"(/q/ to exit) Body Line {i} >>> ")
        if line.strip() == "/q/":
            break
        body.append(line + "\n")
        i += 1
    for item in body:
        message += item
    print(message)
    print("sending mail..")
    return f"mail {message}"

cmds = {"create (box name)": "creates a mailbox", "get box": "displays all mailboxes", 
"select (box name)": "selects the mailbox you want to use", "get mail": "displays the mail from your choosen mailbox", 
"open (mail name)": "reads a specific email", "mail": "opens the mail UI", "remove (mail name)": "removes a mail by name or index"}

client_start()
