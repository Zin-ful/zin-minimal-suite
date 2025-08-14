from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import time
import base64
import curses
from curses import wrapper
from curses.textpad import Textbox
import threading as task
print("REMINDER:\nadd / to the beginning of download path config if not found\n")

"""default vars"""
#some vars loaded in config
height = 0
width = 0
pos = 0
offset = 0
ylimit = 6
colors = {}
screens = {}

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
ACK = 'ACK'
parameters = {"download": download_path}
server = netcom.socket(ipv4, tcp) #creates and defines sock obj

flags = {"-dw": "#*$^||", "-dr": "^($#||", "-t": "#%&$||", "-l": "*@%#||", "-c": "!)$@||", "-mk": "(!%)||", "-gf": "!@%^||"}

cmd_list = ["get file list", "browse","download file","upload file", "make folder", "login","logout", "create", "promote","demote","games","msg", "server test", "client test", "config", "help","exit"]

"""first start process"""
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


"""GUI functions"""

def main(stdscr):
    global height, width, colors
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)

    stdscr.clear()
    stdscr.refresh()
    top_bar = curses.newwin(0, width, 0, 0)
    main_win = curses.newwin(height - 5, width, 2, 0)
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    tbox = Textbox(user_input)
    screens.update({"top": top_bar})
    screens.update({"main": main_win})
    screens.update({"box": user_input})
    screens.update({"text": tbox})
    screens.update({"source": stdscr})
    colors.update({"highlight": highlight})
    init_server(screens, colors)
    menu(screens, colors)
    
def inps(screens, colors):
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            select(key, screens, colors)
        elif key == ord("e"):
            return cmd_list[pos]

def select(key, screens, colors):
    global pos
    if key == ord("s"):
        pos += 1
        if pos >= len(cmd_list):
            pos = len(cmd_list) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    screens["main"].addstr(pos + offset - back, 0, cmd_list[pos - back])
    screens["main"].addstr(pos + offset, 0, cmd_list[pos], colors["highlight"])

#+++helper funcs
def print_text(clr, screens, colors, string, y, x):
    if clr:
        screens["main"].clear()    
    to_print = []
    for char in string:
        if char == '\n':
            text, string = string.split('\n', 1)
            to_print.append(text)
    to_print.append(string)
    for item in to_print:
        if y >= height - 5:
            break
        screens["main"].addstr(y, x, item)
        y += 1
    screens["main"].refresh()

def print_list(clr, screens, colors, text_list, y, x):
    if clr:
        screens["main"].clear()
    to_print = []
    for item in text_list:
        while '\n' in item:
            for char in item:
                if char == '\n':
                    text, item = item.split('\n', 1)
                    to_print.append(text)
            to_print.append(item)
    for item in text_list:
        if y >= height - 5:
            break
        screens["main"].addstr(y, x, item)
        y += 1
    screens["main"].refresh()

def get_input(screens):
    screens["box"].clear()
    inp = screens["text"].edit().strip()
    if inp:
        screens["box"].clear()
        screens["box"].refresh()
        return inp

def getmid(string):
    return width // 2 - len(string) // 2

"""server junk"""
def init_server(screens, colors):
    global ack, server
    if server == None:
        server = netcom.socket(ipv4, tcp)
    msg = f'trying {IP}:{PORT}'
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    time.sleep(0.7)
    try:
        server.connect((IP, PORT))
        msg = "connected, moving to shell.."
        print_text(1, screens, colors, msg, height // 3, getmid(msg))
        server.send(ACK.encode("utf-8"))
        time.sleep(0.5)
        return
    except Exception as e:
        msg = f"error: {e}"
        print_text(0, screens, colors, msg, height // 3, getmid(msg))
        msg = "lost connection to server. do you want to retry?"
        print_text(0, screens, colors, msg, height // 3 + 3, getmid(msg))
        inp = get_input(screens)
        if "y" in inp:
            if server.fileno() != -1:
                msg = "attempting shutdown..."
                print_text(1, screens, colors, msg, height // 3 + 3, getmid(msg))
                time.sleep(0.5)
                try:
                    server.shutdown(netcom.SHUT_RDWR)
                except OSError:
                    msg = "No endpoint to shutdown. Closing server"
                    print_text(1, screens, colors, msg, height // 3 + 3, getmid(msg))
                    time.sleep(1)
                server.close()
            msg = "retrying... (waiting for server, be patient)"
            print_text(1, screens, colors, msg, height // 3, getmid(msg))
            time.sleep(6)
            init_server(screens, colors)
        else:
            server.close()
            exit()

def menu(screens, colors):
    while True:
        exec_success = 0
        print_list(1, screens, colors, cmd_list, 0, 0)
        inp = inps(screens, colors)
        for item, value in cmd_dict.items():
            if inp == item:
                exec_success = value(screens)
                break
        if exec_success:
            continue
        for item, value in client_cmd_dict.items():
            if inp == item:
                exec_success = value(screens)
                break
        if exec_success:
            continue
        send(screens, inp, 0)
        flag, response = receive(screens, 0)
        print_text(1, screens, colors, response, 1, getmid(response))
        userwait(screens)

"""helper functions"""

def userwait(screens):
    key = screens["main"].getch()
    if key:
        pass

def server_exec(screens, data):
    return

def file_write(screens, data):
    ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
    file_name, data = data.split("!:DATA:!")
    trash, file_ext = file_name.split(".")
    if any(file_name in files for files in os.listdir(download_path)):
        msg = f"file already exists, press e to continue"
        print_text(1, screens, colors, msg, height // 3, getmid(msg))
        key = screens["main"].getch()
        if key:
            pass
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
            msg = f"file failed to download due to these reasons: {e}"
            print_text(1, screens, colors, msg, height // 3, getmid(msg))
            key = screens["main"].getch()
            if key:
                pass
    msg = "file downloaded"
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    key = screens["main"].getch()
    if key:
        pass

def file_read(screens, inp):
    ext_list = [".txt",".py",".c",".md",".log",".cpp",".h",".hpp",".java",".cs",".js",".ts",".php",".sh",".rb",".pl",".go",".rs",".asm","sql"]
    cmd, file_path = inp.split(' ')
    check_slsh = list(file_path)
    if check_slsh[0] != "/":
        file_path = "/" + file_path
    msg = f"press 'e' to confirm, 'q' to reject to confirm file path: {file_path}"
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    key = screens["main"].getch()
    if key:
        pass
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
    if any(file_name in files for files in os.listdir(check_path)):
        msg = "that file does not exist, press any key to continue"
        print_text(1, screens, colors, msg, height // 3, getmid(msg))
        key = screens["main"].getch()
        if key:
            pass
        return
    if any(file_ext in files for files in ext_list):
        with open(file_path, 'r') as file:
            filedata = file.read()
            data_send(screens, f"{cmd} {file_name}!:DATA:!{filedata}")
    else:
        with open(file_path, 'rb') as file:
            filedata = file.read()
            filedata = base64.b64encode(filedata).decode('utf-8')
            data_send(screens, f"{cmd} {file_name}!:DATA:!{filedata}")

def send(screens, data, encoded):
    is_flagged = "n"
    msg = "checking flag.."
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    time.sleep(0.5)
    for key, val in flags.items():
        if val in data:
            is_flagged = "y"
            msg = f"is flagged: {val}"
            print_text(1, screens, None, msg, height // 3, getmid(msg))
            time.sleep(0.5)
    head = str(len(data + is_flagged)).zfill(header_size)
    data = head + is_flagged + data
    msg = "data send."
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    time.sleep(0.5)
    server.send(data.encode("utf-8"))
    ack(0)

def receive(screens, encoded):
    data_received = b''
    msg = "receiving header.."
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    time.sleep(0.5)
    packet_size = server.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    msg = f"header size is: {packet_size}"
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    time.sleep(0.5)
    is_flagged = server.recv(1).decode("utf-8")
    if is_flagged == "y":
        msg = "is flagged."
        print_text(1, screens, None, msg, height // 3, getmid(msg))
        flag = server.recv(6).decode("utf-8").strip("||")
    else:
        msg = "is not flagged."
        print_text(1, screens, None, msg, height // 3, getmid(msg))
        flag = None
    time.sleep(0.5)
    while len(data_received) < packet_size:
        data_received += server.recv(packet_size - len(data_received))
        msg = f"data being received: {packet_size} | {len(data_received)} = {data_received}"
        print_text(1, screens, None, msg, height // 3, getmid(msg))
        time.sleep(0.3)
    ack(1)
    msg = f"data received: {data_received}"
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    time.sleep(0.5)
    data_received = data_received.decode("utf-8")
    return flag, data_received

def ack(state):
    if not state:
        ack_acpt = server.recv(3).decode("utf-8")
    else:
        server.send(ACK.encode('utf-8'))

def format_list(data):

"""user functions"""
def login(screens):
    msg = "Enter your login information. Format: 'name username password'"
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    login_info = get_input(screens)
    send(screens, flags["-l"]+"/"+login_info, 0)
    flag, response = receive(screens, 0)
    print_text(1, screens, None, response, height // 3, getmid(response))
    userwait(screens)
    return 1

def logout(screens):
    global server
    msg = "Youve logged out, connect back?"
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    inp = get_input(screens)
    if "y" in usr_inp:
        msg = "trying to connect... (waiting for server, be patient)"
        print_text(1, screens, colors, msg, height // 3, getmid(msg))
        time.sleep(5)
        if server.fileno() != -1:
            server.close()
            server = None
        time.sleep(1)
        cmd()
    else:
        exit()

def create(screens):
    msg = "Enter your desired account information. 'Format: name username password'"
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    login_info = get_input(screens)
    send(screens, flags["-c"]+"/"+login_info, 0)
    flag, response = receive(screens, 0)
    print_text(1, screens, None, response, height // 3, getmid(response))
    userwait(screens)
    return 1

def test(screens):
    for i in range(10):
        send(screens, flags["-t"]+f"Packet: {i}", 0)
        flag, data_received = receive(screens, 0)
        msg = f"Testing packet: {i}\n{data_received}"
        print_text(1, screens, colors, msg, height // 3, getmid(msg))
    return 1

def config(screens):
    global parameters
    param_list = []
    for name, item in parameters.items():
        param_list.append(f"{name} = {item}")
    msg = "Select a name to edit that configuration"
    print_text(1, screens, colors, msg, 0, getmid(msg))
    print_list(0, screens, colors, param_list, 1, 0)
    inp = get_input(screens)
    for name, item in parameters.items():
        if inp == name:
            msg = f"what would you like to set the value of {name}?"
            print_text(1, screens, colors, msg, 0, getmid(msg))
            inp = get_input(screens)
            parameters[name] = inp
    with open(config_path, "w") as file:
        for name, item in parameters.items():
            if name == "download":
                if item[len(item) - 1] != "/":
                    item += "/"
            file.write(f"{name}={item}")
    msg = "config saved. press any key to continue"
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    key = screens["main"].getch()
    if key:
        pass

def make_directory(screens):
    msg = "what folder would you like to create?"
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    folder_name = get_input(screens)
    msg = "(press enter to create at root or '/') which parent folder would you like to create this in? (folder needs to exist first)"
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    folder_path = get_input(screens)
    if not folder_path:
        if folder_name[0] != "/":
            full_path = "/"+folder_name
        else:
            full_path = folder_name
    else:
        if folder_path[0] == "/":
            folder_path = folder_path.strip("/", 1)
        if folder_name[0] != "/":
            folder_name = "/"+folder_name
        full_path = folder_path+folder_name
    send(screens, flags["-mk"]+full_path, 0)
    flag, response = receive(screens, 0)
    print_text(1, screens, colors, response, height // 3, getmid(response))
    userwait(screens)
    return 1

def browse_files(screens):
    get_file_tree(screens)
    return 1
    file_tree = {}
    with open("file_tree.conf", "r") as file:
        tree_data = file.readlines()
        for item in tree_data:
            file_temp = []
            path, files = item.split(":")
            files_cpy = files
            for char in files_cpy:
                if char == ",":
                    file_name, files = files.split(",", 1)
                    file_temp.append(file_name)
            file_tree.update({path:file_temp})
            
def get_file_tree(screens):
    send(screens, flags["-gf"]+'ack', 0)
    flag, response = receive(screens, 0)
    if "." not in response

    

client_cmd_dict = {"config": config, "browse": browse_files}
cmd_dict = {"login": login, "logout": logout, "create": create, "testing": test, "make folder": make_directory}

wrapper(main)
