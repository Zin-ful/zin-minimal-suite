from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import time
import base64
print("REMINDER:\nadd / to the beginning of download path config if not found\n")

"""default vars"""
#some vars loaded in config
header_size = 100
IP = 'localhost'
PORT = 12345
download_path = os.path.expanduser("`/")
auto_name = 'none'
auto_user = 'none'
auto_pass = 'none'
auto_enabled = "false"
firstboot = "true"
config_dir = '/etc/zfile'
config_path = '/etc/zfile/config.conf'
user_config_path = "/etc/zfile/autouser.conf"
root = os.path.expanduser("~")
ack = 'ACK'
parameters = {"download": download_path, "auto": auto_enabled, "aname": auto_name, "auser":auto_user, "apass": auto_pass, "boot": firstboot}
server_conn = netcom.socket(ipv4, tcp) #creates and defines sock obj
server_cmd_list = ["config", "help","exit","promote","demote","create","login","logout","games","msg"]

"""checking for configuration, mostly for first setup'"""
if "zfile" not in os.listdir("/etc"):
    os.makedirs(config_dir, exist_ok=True)
if "zfile.conf" not in os.listdir(config_dir):
    with open(config_path, "w") as file:
        for name, item in parameters.items():
            file.write(f"{name}={item}")
else:
    with open(config_path, "r") as file:
        params = file.readlines()
        for item in params:
            name, data = item.split("=")
            if name == "download":
                if data[len(data) - 1] != "/":
                    data += "/"
            parameters[name.strip()] = data.strip()


"""basiclly main()"""
def cmd():
    global ack, server_conn
    if server_conn == None:
        server_conn = netcom.socket(ipv4, tcp)
    print(f'trying {IP},{PORT}')
    try:
        server_conn.connect((IP, PORT))
        print("connected, type 'help' for more information")
        server_conn.send(ack.encode("utf-8"))
        while True:
            print()
            usr_inp = input(">>> ")
            usr_inp.strip()
            if "send" in usr_inp or "update" in usr_inp:
                file_read(usr_inp)
                continue
            for i in server_cmd_list:
                if usr_inp == i:
                    usr_inp += "|"
            data = data_send(usr_inp)
            if "login|" in usr_inp and parameters["auto" == "true":
                login()
            elif "!:DATA:!" in data:
                file_write(data)
    except TimeoutError:
        if not confirmrecv:
            print('no data recv')
    except Exception as e:
        print(f"error: {e}")
        usr_inp = input("lost connection to server. do you want to retry?\n>>> ")
        if "y" in usr_inp:
            if server_conn.fileno() != -1:
                server_conn.shutdown(netcom.SHUT_RDWR)
                server_conn.close()
            print("retrying... (waiting for server, be patient) ")
            time.sleep(6)
            cmd()
        else:
            server_conn.close()
            exit()

"""misc functions"""
#we lessen the load on the client by having the server do most of the work, however the client still has actions to perform
#to lessen network usage, the server formats (using forloops instead of str(list)) omitting uneeded chars
#also to make things more readable, we store simple (or complex) tasks in functions to make debugging easier
def config(*arg):
    global parameters
    for name, item in parameters.items():
        print("{name} = {item}")
    print("Select a name to edit that configuration")
    inp = input(">>> ")
    for name, item in parameters.items():
        if inp == name:
            inp = input("what would you like to set the value of {name}?\n>>> ")
            parameters[name] = inp
    with open(config_path, "w") as file:
        for name, item in parameters.items():
            if name == "download":
                if item[len(item) - 1] != "/":
                    item += "/"
            file.write(f"{name}={item}")

def file_write(data):
    ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
    file_name, data = data.split("!:DATA:!")
    trash, file_ext = file_name.split(".")
    if any(file_name in files for files in os.listdir(download_path)):
        print("file already exists")
    elif not any(file_name in files for files in os.listdir(download_path)):
        try:
            if any(file_ext in files for files in ext_list):
                with open(f"{parameters['download']}{file_name}", "w") as file:
                    file.write(data)
            else:
                data = base64.b64decode(data)
                with open(f"{parameters['download']}{file_name}", "wb") as file:
                    file.write(data)
        except Exception as e:
            print(f"file failed to download due to these reasons: {e}")
    print("file downloaded")
def login():
    global auto_enabled, parameters
    if parameters["boot"] == "false" and parameters["auto"] == "true":
        login_info = f"{parameters['aname']} {parameters['auser']} {parameters['apass']}"
        parameters["auto"] = "false"
    elif parameters["boot"] == "false" and parameters["auto"] == "false":
        login_info = input(">>> ")
    else:
        login_info = input(">>> ")
        parameters["aname"], parameters["auser"], parameters["apass"] = login_info.split(' ')
        with open(config_path, "w") as file:
            for item, val in parameters.items():
                file.write(f"{item}={val}")
    data_send(login_info)

def logout():
    global server_conn
    usr_inp = input("youve logged out. Would you like to connect back?")
    if "y" in usr_inp:
        print("trying to connect... (waiting for server, be patient)")
        time.sleep(5)
        if server_conn.fileno() != -1:
            server_conn.close()
            server_conn = None
        time.sleep(1)
        cmd()
    else:
        exit()

def file_read(usr_inp):
    ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
    cmd, file_path = usr_inp.split(' ')
    check_slsh = list(file_path)
    if check_slsh[0] != "/":
        file_path = "/" + file_path
    print(file_path)
    file_path = root + file_path
    file_name = ''
    total = 0
    for i in file_path:
        if i == "/":
            total += 1 #couldnt figure out how to get the total and compare with count in the same loop
    count = 0
    for i in file_path:
        if i == "/":
            count += 1
        if count == total:
            file_name += i #might be hard to figure out how it works so ill leave this bad comment that explains the code
                                     #basically, we count the amount of slashes to get a total. then we count again but once we reach the total we start adding the letters in file_path to file_name
                                     #this way we can handle files in any directory post /~
    _, file_ext = file_name.split(".")
    check_path = file_path.replace(file_name, '')
    print(check_path)
    if any(file_name in files for files in os.listdir(check_path)):
        print("that file does not exist")
        return
    if any(file_ext in files for files in ext_list):
        with open(file_path, 'r') as file:
            filedata = file.read()
            print(f"{cmd} {file_name}!:DATA:!".encode("utf-8"))
            print(f"{cmd} {file_name}!:DATA:!")
            data_send(f"{cmd} {file_name}!:DATA:!{filedata}")
    else:
        with open(file_path, 'rb') as file:
            filedata = file.read()
            filedata = base64.b64encode(filedata).decode('utf-8')
            data_send(f"{cmd} {file_name}!:DATA:!{filedata}")

def data_send(usr_inp):
    header = str(len(usr_inp)).zfill(header_size) #can get up to ten places worth of bytes, adjust as needed
    to_send = str(header) + usr_inp
    server_conn.send(to_send.encode("utf-8"))
    ack_acpt = server_conn.recv(3).decode("utf-8")
    pck_sze = server_conn.recv(header_size).decode("utf-8")
    pck_sze = int(pck_sze)
    data = b''
    while len(data) < pck_sze:
        data += server_conn.recv(pck_sze - len(data))
    data = data.decode("utf-8")
    if "!:DATA:!" in data:
        pass
    elif "logged out" in data:
        server_conn.shutdown(netcom.SHUT_RDWR)
        logout()
    else:
        print(data)
    server_conn.send(ack.encode("utf-8"))
    return data
cmd()
