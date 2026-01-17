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

"""default vars"""
#some vars loaded in config
height = 0
width = 0
pos = 0
offset = 0
ylimit = 6
colors = {}
screens = {}
win = {}

header_size = 100
IP = 'localhost'
PORT = 25415
download_path = os.path.expanduser("~")
auto_name = 'none'
auto_user = 'none'
auto_pass = 'none'
auto_enabled = "false"
firstboot = "true"
root = os.path.expanduser("~")
config_dir = root+'/.zinapp/zfile'
config_path = root+'/.zinapp/zfile/zfile.conf'
user_config_path = root+"/.zinapp/zfile/autouser.conf"
ACK = 'ACK'
parameters = {"download": download_path}
server = netcom.socket(ipv4, tcp) #creates and defines sock obj

flags = {"-rf": "#*$^||", "-sf": "^($#||", "-t": "#%&$||", "-l": "*@%#||", "-c": "!)$@||", "-mk": "(!%)||", "-br": "*!&_"}
cmd_extras = ["browse", "promote","demote", "server test", "client test", "help", "config", "logout", "exit"]
cmd_list = ["login", "create", "config", "exit"]

"""first start process"""
if "zfile" not in os.listdir(root+"/.zinapp"):
    os.mkdir(config_dir)
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
    global height, width, colors, win
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
    files_win = curses.newwin(height - 4, width - 1, 2, 0)
    win = {"main": stdscr, "files": files_win}
    init_server(screens, colors)
    menu(screens, colors)
    
def inps(listy):
    pos = 0
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            pos = select(pos, key, listy)
            if not pos:
                pos = 0
        elif key == ord("e"):
            return listy[pos]

def select(pos, key, listy):
    if key == ord("s"):
        pos += 1
        if pos >= len(listy):
            pos = len(listy) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    screens["main"].addstr(pos + offset - back, 0, listy[pos - back])
    screens["main"].addstr(pos + offset, 0, listy[pos], colors["highlight"])

def init_browse():
    send(screens, "" 0) #need to send data first
    while True:
        current_path = receive(screens, 0)
        if current_path == "#None":
            print_text(1, "No files in directory", width // 2, height // 3)
            user_wait(screens)
            choice = simple_input(screens["main"], ["Upload File", "Create Directory", "Exit"])
            if "Upload" in choice:
                upload() #confirm this works
            elif "Create" in choice:
                make_directory(screens) #confirm this works
            else:
                send(screens, "br", 0)
                return
            continue
        choice = None#make new input that includes custom keybinds supplied with dictionary
        #use keybinds here to control user_input
def upload():
    path = get_file()
    path, name = path.split(":")
    screens["source"].clear()
    msg = f"Confirm path?: {path+'/'+name}"
    screens["source"].clear()
    screens["source"].addstr(0 ,getmid(msg),msg)
    screens["source"].refresh()
    userwait(screens)
    send(screens, flags["-dw"]+name, 0)
    send_file(screens, path+"/"+name)
    flag, response = receive(screens, 0)
    print_text(1, screens, None, response, height // 2, getmid(response))
    userwait(screens)
    screens["source"].clear()
    return 1

#+++helper funcs
def simple_input(screen, menu):
    pos = 0
    print_list(1, menu, 0, 0)
    screen.refresh()
    while True:
        if not pos:
            pos = 0
        key = screen.getch()
        if key == ord("s") or key == ord("w"):
            pos = select(pos, key, screen, menu)
        elif key == ord("e"):
            return menu[pos]
        elif key == ord("q"):
            return

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

def print_list(clr, text_list, y, x):
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
        print_list(1, cmd_list, 0, 0)
        inp = inps(cmd_list)
        for item, value in cmd_dict.items():
            if inp == item:
                exec_success = value()
                break
        if exec_success:
            continue
        for item, value in client_cmd_dict.items():
            if inp == item:
                exec_success = value()
                break
        if exec_success:
            continue
        send(screens, inp, 0)
        flag, response = receive(screens, 0)
        print_text(1, screens, colors, response, 1, getmid(response))
        userwait(screens)

"""helper functions"""
def update_functions(response):
    if "Welcome" in response:
        cmd_list.remove("login")
        cmd_list.remove("create")
        cmd_list.remove("exit")
        cmd_list.remove("config")
        for item in cmd_extras:
            cmd_list.append(item)

def userwait(screens):
    key = screens["main"].getch()
    if key:
        pass

def receive_file(screens, path):
    part_size = 4096
    packet_size = server.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    ack(1)
    with open(path, "wb") as file:
        while data_received < packet_size:
            data_received = packet_size - data_received
            part = server.recv(min(part_size, data_received))
            if not part:
                break
            file.write(part)
            data_received += len(part)
    ack(1)

def send_file(screens, path):
    with open(path, "rb") as file:
        file.seek(0, 2)
        file_size = file.tell()
    head = str(file_size).zfill(header_size)
    msg = f"file size {header_size}, sending..."
    print_text(1, screens, None, msg, height // 3, getmid(msg))
    time.sleep(0.5)
    server.send(str(head).encode("utf-8"))
    ack(0)
    with open(path, "rb") as file:
        i = 0
        while True:
            part = file.read(4096)
            if not part:
                break
            msg = f"sending part {i}"
            print_text(1, screens, None, msg, height // 3, getmid(msg))
            time.sleep(0.001)
            server.send(part)
            i += 1
    ack(0)

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

"""user functions"""

def login():
    msg = "Enter your login information. Format: 'name username password'"
    print_text(1, screens, colors, msg, height // 3, getmid(msg))
    login_info = get_input(screens)
    send(screens, flags["-l"]+"/"+login_info, 0)
    flag, response = receive(screens, 0)
    update_functions(response)
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
    update_functions(response)
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
        return 1

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

def itemize_list(listy):
    file_temp = []
    listy_cpy = listy
    for char in listy_cpy:
        if char == ",":
            file_name, listy = listy.split(",", 1)
            file_temp.append(file_name)
    return file_temp   


client_cmd_dict = {"config": config, "browse": init_browse}
cmd_dict = {"login": login, "logout": logout, "testing": test}

"""CODE FROM FILE BROWSER"""

data_name = ""
data_path = ""

pos = 0
sx = 0
lvl = 0
origin = 0
num = 0

ylimit = 4

cur_dir = "/home"
files_in_path = os.listdir(cur_dir)
SELECT = None
data = None
hidden = 1

def list_file(delay, rst):
    global origin, files_in_path, pos, sx, lvl, num
    time.sleep(0.1)
    win["files"].clear()
    files_in_path = os.listdir(cur_dir)
    if rst:
        pos = 0
        lvl = 0
        num = 0
    sx = 0
    i = 0
    y = 0
    x = 0
    for item in files_in_path.copy():
        if item[0] == "." and hidden:
            files_in_path.remove(item)
    for item in files_in_path:
        if num * (height - ylimit) + i >= len(files_in_path):
            break
        if x >= width - 5:
            return
        else:
            win["files"].addstr(y, x, files_in_path[num * (height - ylimit) + i], curses.COLOR_WHITE)
        i += 1
        y += 1
        if y >= height - ylimit:
            x += width // 3
            y = 0
        time.sleep(delay)
        win["files"].refresh()

def get_file():
    global cur_dir, pos, origin
    win["main"].clear()
    win["main"].refresh()
    list_file(0.001, 1)
    while True:
        key = win["files"].getch()
        if key == -1:
            continue
        if key == ord("a") or key == ord("d"):
            cur_dir = move(key)
            list_file(0.002, 1)
            win["files"].refresh()
        elif key == ord("w") or key == ord("s"):
            select_file(key, "files", files_in_path, None)
        elif key == ord("e"):
            return cur_dir+":"+files_in_path[pos]
        elif key == ord('q'):
            return

def select_file(inp, subwin, word_list, xoffset):
    global pos, sx, lvl, num
    if not xoffset:
        xoffset = 0
    if not word_list or len(word_list) < 0:
        win[subwin].addstr(1, 0, "NO FILES IN PATH", curses.COLOR_RED)
        win[subwin].refresh()
        return
    if inp == ord("s"):
        pos += 1
        offset = 1
    elif inp == ord("w"):
        offset = -1
        pos -= 1
    prevlen = ""
    if pos >= height - ylimit and len(word_list) > height - ylimit and subwin == "files":
        pos = 0
        lvl += 1
        sx += width // 3
        if sx >= width - 3:
            if sx // width == 0:
                num += 3
            else:
                num += 3
            list_file(win, 0.002, 0)
    elif pos == -1 and lvl >= 1 and subwin == "files":
        sx -= width // 3
        pos = height - ylimit - 1
        lvl -= 1
        if sx < 0 and num:
            num -= 3
            list_file(0.002, 0)
            sx = (width - width // 3)

    if pos <= 0:
        offset = 0
        pos = 0
    elif pos >= len(word_list):
        pos = len(word_list) - 1
        offset = 0
    for i in word_list[pos]:
        prevlen += " "
    if lvl:
        lvl_offset = (height - ylimit) * lvl
    else:
        lvl_offset = 0
    if pos + lvl_offset >= len(files_in_path) and subwin == "files":
        pos -= 1
    final_pos = origin + pos - offset
    if subwin == "files":
        if pos > -1:
            if  final_pos >= height - ylimit or final_pos >= len(files_in_path):
                pass
            else:
                win[subwin].addstr(final_pos, sx + xoffset, prevlen, curses.COLOR_BLACK)
                win[subwin].addstr(final_pos, sx + xoffset, word_list[pos - offset + lvl_offset], curses.COLOR_BLACK)
        win[subwin].addstr(origin + pos, sx + xoffset, word_list[pos + lvl_offset])
    else:
        if pos > -1:
            win[subwin].addstr(final_pos, sx + xoffset, prevlen, curses.COLOR_BLACK)
            win[subwin].addstr(final_pos, sx + xoffset, word_list[pos - offset], curses.COLOR_BLACK)
        win[subwin].addstr(origin + pos, sx + xoffset, word_list[pos])
    win[subwin].refresh()

def move(inp):
    rev_dir = os.path.dirname(f"{cur_dir}..")
    if files_in_path or len(files_in_path) > 0:
        if cur_dir == "/":
            forw_dir = cur_dir + files_in_path[num * sx + pos]
        else:
            if not num and sx:
                calc = (lvl * (height - ylimit)) + pos
                forw_dir = cur_dir + "/" + files_in_path[calc]
            else:
                calc = (lvl * (height - ylimit)) + pos
                forw_dir = cur_dir + "/" + files_in_path[calc]
    if inp == ord("a"):
        if cur_dir == "/":
            return "/"
        else:
            try:
                var = os.listdir(rev_dir)
            except:
                return cur_dir
            return rev_dir
    elif inp == ord("d"):
        try:
            var = os.listdir(forw_dir)
        except:
            return cur_dir
        return forw_dir


wrapper(main)

