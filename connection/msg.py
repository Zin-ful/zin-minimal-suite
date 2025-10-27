from socket import SOCK_STREAM as tcp
from socket import AF_INET as ipv4
import socket as netcom
import os
import threading as task
import time
import sys

curusr = os.path.expanduser("~")

session_usr = []
conf_path = curusr+ "/.zinapp/ztext"
username = "none"
alias = "none"
autoconn = "false"
users = 0
ready = 0
ipid = "none"
network = ""
security = ""
port = 34983
ip = ""
msg = ''
y = 0
server = ''
qkeys = {}
pause = 0
msgbreak = "----------------------"
attr_dict = {"ipaddr": ip, "name": username, "autoconnect": autoconn, "idaddr": ipid, "alias":alias}

if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "ztext" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(curusr+"/.zinapp/ztext")
if "phonebook" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(curusr+"/.zinapp/phonebook")

def message_recv():
    global y, msg, users
    x = 0
    while True:
        num = 0
        msg = server.recv(2048)
        if pause:
            continue
        if msg:
            msg = msg.decode("utf-8")
            y += 1
            if "@" in msg:
                recvusr, msg = msg.split(":", 1)
                recvusr = recvusr.strip("@").strip()
                if recvusr not in session_usr:
                    session_usr.append(recvusr)
                msg = f"{getnick(recvusr)}{msg}"

            if "server.message.from.server" in msg:
                msg = msg.replace("server.message.from.server", "")
                response, msg = msg.split(".", 1)
                if "users:" in msg:
                    response, msg = msg.split("!")
                    response = response.strip("users:")
                    users += int(response.strip())
                print(f"{msg}\n{msgbreak}")
            else:
                print(f"{msg}\n{msgbreak}")
               
def getnick(name):
    if "@" in name:
        name = name.strip("@")
    if f"{name}.txt" not in os.listdir(curusr+"/.zinapp/phonebook"):
        return f"@{name}:"
    with open(curusr+f"/.zinapp/phonebook/{name}.txt", "r") as file:
        data = file.readlines()
        for item in data:
            if "nickname:" in item:
                item = item.strip("nickname:").strip()
                return f"@{item}:"
    return f"@{name}:"

def query():
    success = 0
    print("Users: ")
    names = os.listdir(curusr+"/.zinapp/phonebook")
    for name in names:
        print(name.strip(".txt"))
    print("Whos contact would you like to view?")
    inp = input("(Contact) >>> ")
    if inp:
        for item in names:
            if inp.lower() == item.strip(".txt").lower() or inp.strip("@").lower() == item.strip(".py").strip("@").lower():
                with open(f"/etc/phonebook/{item}", "r") as file:
                    data = file.readlines()
                    for item in data:
                        print(item)
                success = 1
    if not success:
        show_chat.addstr(y + 1, 0, "User does not exist", HIGHLIGHT_1)
        show_chat.refresh()
        time.sleep(1)
    
def savenick():
    global pause
    if not session_usr:
        return
    success = 0
    pause = 1
    print("Users:")
    for name in session_usr:
        print(name)
    print("Who would you like to add to your contacts?")
    inp = input("(Contact) >>> ")
    if inp:
        for name in session_usr:
            if inp.lower() == name.lower() or name.strip("@").lower() == inp.strip("@").lower():
                data = []
                print("Were going to fill out information for this user.")
                inp = input("Name: ")
                if inp:
                    if "@" in inp:
                        inp = inp.strip("@")
                    newname = inp
                    data.append(inp)
                
                inp = input("Nickname: ")
                if inp: 
                    data.append(inp)
                inp = input("IP Address: ")
                if inp:
                    data.append(inp)
                inp = input("Notes: ")
                if inp:
                    data.append(inp)
                with open(f"/etc/phonebook/{newname}.txt", "w") as file:
                    file.write(f"name: {data[0]}\n")
                    file.write(f"nickname: {data[1]}\n")
                    file.write(f"ip address: {data[2]}\n")
                    file.write(f"notes: {data[3]}\n")
                    success = 1
    
    if success:
        msg = "Writing to file, please wait..."
    else:
        msg = "User does not exist. Exiting..."
    print(msg)
    pause = 0
    

"""user functions"""

def shutoff():
    print("exiting...")
    message_thread.join(timeout=1)
    server.close()
    sys.exit()

def listcmd():
    for item in commands:
        result = item + "\n"
    return result

def auto_conf():
    global autoconn
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        state = file.readlines()
        for item in state:
            if "autoconnect" in item:
                trash, bl = item.split("=")
                break
        if "true" in bl:
            attr_dict["autoconnect"] = "false"
        else:
            attr_dict["autoconnect"] = "true"
    with open(f"{conf_path}/msg_server.conf", "w") as file:
        for title, val in attr_dict.items():
            file.write(f"{title}={val}\n")
    return f"autoconnect set to {attr_dict['autoconnect']}"

def changeuser():
    msg = "What would your username like to be?"
    inp = input("(Config) >>> ")
    print("Writing to file, please wait...")
    if inp:
        attr_dict["name"] = inp.strip()
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, val in attr_dict.items():
                file.write(f"{title}={val}\n")
    time.sleep(1)
    print("Username updated!")

def set_qkeys():
    with open(""):
        return

def importip():
    global ipid, alias
    print("This will assist you in connecting to networks")
    print("We will assign an ID to an IP address")
    print("please enter the IP address youd like to give an ID")
    inp = input("(Config) >>> ")
    if inp:
        attr_dict["idaddr"] = inp.strip()
    print("For the ID, you can enter any number or text")
    print("You can only have one ID total")
    print("please enter the ID to be assigned")
    inp = input("(Config) >>> ")
    if inp:
        attr_dict["alias"] = inp.strip()
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, val in attr_dict.items():
                file.write(f"{title}={val}\n")
    print("Writing to file, please wait...")
    time.sleep(1)
    print("Connection ID added. To skip the connection process entirely, configure #autostart")
    
commands = {"#help": listcmd, "#exit": shutoff, "#query-user": query, "#add-user": savenick, "#change-user": changeuser, "#autoconnect":auto_conf, "#import-ip":importip}

#$
def message():
    while True:
        try:
            inp = input(f"{msgbreak}\n")
            if inp:
                if "#" in inp and '"' not in inp:
                    xcute = commands.get(inp)
                    if xcute:
                        inp = xcute()
                    else:
                        inp = "invalid"
                    if inp:
                        print(inp)
                        print(msgbreak)
                    inp = None
                    continue
                
                server.sendall(inp.encode("utf-8"))
                inp = None
        except KeyboardInterrupt:
                server.close()
                exit()
        except Exception as e:
            print(e)

def config_init():
    global ip, username, network, server, autoconn, ipid, alias
    try:
        with open(f"{conf_path}/msg_server.conf", "r") as file:
            attr = file.readlines()
            for item in attr:
                if item == "\n":
                    pass
                else:
                    item, attr = item.split("=")
                    attr_dict[item.strip()] = attr.strip()
            if attr_dict["autoconnect"] == "true":
                autoconnect(show_chat, user_input, tbox)
            else:
                manual_conf("false")
    except Exception as e:
        with open(f"{conf_path}/errlog.txt", "a") as file:
            file.write(f"ERROR ERROR ERROR\n\n{str(e)}\n\n")
            for name, val in attr_dict.items():
                file.write(f"attr: {name} = {val}")
            file.write(f"ERROR END\n")
        manual_conf("true")

def manual_conf(state):
    global ip, username, network, server
    os.makedirs(conf_path, exist_ok=True)
    if state == "true":
        print("It looks like its your first time starting the messenger.")
        print("Lets start by getting the username youd like to use")
    print("please enter your desired username")
    inp = input("(Config) >>> ")
    if inp:
        attr_dict["name"] = inp.strip()
    if state == "true":
        print("Next enter the IP address of the message server your connecting to")
        print("If you are hosting the server yourself, 'localhost' will work")
    print("please enter the IP to connect to")
    inp = input("(Config) >>> ")
    if inp:
        attr_dict["ipaddr"] = inp.strip()
    if state == "true":
        print("Writing to file, please wait...")
    time.sleep(1)
    print("Attempting connect. To skip the connection process entirely, configure #autostart")
    if state == "true":
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, data in attr_dict.items():
                file.write(f"{title}={data}\n")
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"], port))
    server.sendall(attr_dict["name"].encode("utf-8"))
    network = "connected!    "
    print("Connection accepted! Moving to shell..")

def autoconnect():
    global ip, username, network, server
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attrs = file.readlines()
        for item in attrs:
            title, val = item.split("=")
            attr_dict[title.strip()] = val.strip()
    print(f"Connecting to: {attr_dict['idaddr']}")
    print(f"Username: {attr_dict['name']}")
    print("Waiting for accept...")
    time.sleep(1)
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"], port))
    server.sendall(attr_dict["name"].encode("utf-8"))
    network = "connected!    "
    print("Connection accepted! Moving to shell..")

config_init()
message_thread = task.Thread(target=message_recv, daemon=True)
message_thread.start()
message()
