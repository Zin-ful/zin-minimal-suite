#!/usr/bin/env python3
from socket import SOCK_STREAM as tcp
from socket import AF_INET as ipv4
import socket as netcom
import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys

"""
FIX

Change shitty UI to make it more readable
Add user information to UI such as name, ip address, etc
"""

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
threads_started = 0

main_menu = ["Messenger", "Group Chat"]

attr_dict = {"ipaddr": ip, "name": username, "autoconnect": autoconn, "idaddr": ipid, "alias":alias}

colors = {}
screens = {}

if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "ztext" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(curusr+"/.zinapp/ztext")
if "msg_server.conf" not in os.listdir(curusr+"/.zinapp/ztext"):
    with open(curusr+"/.zinapp/ztext/msg_server.conf", "w") as file:
        for item, val in attr_dict.items():
            file.write(f"{item}={val}\n")

if "phonebook" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(curusr+"/.zinapp/phonebook")

"""utility functions"""

def main(stdscr):
    global height, width, message_thread, update_thread, pause
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)
    HIGHLIGHT = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLUE)
    HIGHLIGHT_1 = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    HIGHLIGHT_2 = curses.color_pair(3)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
    HIGHLIGHT_3 = curses.color_pair(4)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    HIGHLIGHT_4 = curses.color_pair(5)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
    FROM_SERVER = curses.color_pair(6)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)
    ERASE = curses.color_pair(7)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
    TUT = curses.color_pair(8)

    colors.update({"hl":HIGHLIGHT})
    colors.update({"hl1":HIGHLIGHT_1})
    colors.update({"hl2":HIGHLIGHT_2})
    colors.update({"hl3":HIGHLIGHT_3})
    colors.update({"hl4":HIGHLIGHT_4})
    colors.update({"server":FROM_SERVER})
    colors.update({"erase":ERASE})
    colors.update({"tut":TUT})

    stdscr.clear()
    stdscr.refresh()

    top_win = curses.newwin(0, width, 0, 0)
    show_chat = curses.newwin(height - 5, width, 2, 0)
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    tbox = Textbox(user_input)
    screens.update({"bar":top_win})
    screens.update({"chat":show_chat})
    screens.update({"input":user_input})
    screens.update({"text":tbox})
    screens.update({"source":stdscr})
    security = "CHATS ARE NOT ENCRYPTED"
    i = 0
    while i < width:
        screens["bar"].addstr(0, i, " ", HIGHLIGHT)
        i += 1
    success = 0
    pause = 1
    while True:
        ref(stdscr)
        choice = inps(main_menu)
        ref(stdscr)
        if choice == main_menu[0]:
            screens["bar"].refresh()
            if not contact_selection():
                ref(screens["chat"])
                ref(screens["bar"])
                screens["chat"].addstr(5, 0, "No contacts found, add users to your contacts in group chat")
                screens["chat"].addstr(6, 0, "Press any key to continue")
                screens["chat"].refresh()
                screens["chat"].getch()
                continue
        else:
            group_message()

"""menu functions"""
def get_input():
    inp = screens["text"].edit().strip()
    if inp:
        return inp

def inps(menu):
    print_list(0, 0, menu)
    pos = 0
    while True:
        inp = screens["source"].getch()
        if inp == ord("e"):
            return menu[pos]
        elif inp == ord("w") or inp == ord("s"):
            pos = select(menu, inp, pos)
        elif inp == ord("R"):
            screens["source"].clear()
            screens["source"].refresh()
            print_list(0, 0, menu)

def dynamic_inps(menu, offset):
    print_list(0 + offset, 0, menu)
    pos = 0
    while True:
        inp = screens["source"].getch()
        if inp == ord("e"):
            return menu[pos]
        elif inp == ord("w") or inp == ord("s"):
            pos = dynamic_select(menu, inp, pos, offset)
        elif inp == ord("R"):
            screens["source"].clear()
            screens["source"].refresh()
            print_list(0 + offset, 0, menu)

def dynamic_select(menu, key, pos, offset):
    if key == ord("s"):
        pos += 1
        if pos >= len(menu):
            pos = len(menu) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    if len(menu) > 1:
        screens["source"].addstr(pos - back + offset, 0, menu[pos - back])
    screens["source"].addstr(pos + offset, 0, menu[pos], colors["server"])
    return pos


def print_list(y, x, menu):
    i = 0
    for item in menu:
        screens["source"].addstr(y + i, x, item)
        i += 1
    screens["source"].refresh()

def errlog(error):
    with open(conf_path+"/err.txt", "a") as file:
        file.write("\nERROR\nERROR\n")
        for name, value in attr_dict.items():
            file.write(f"{name}:{value}\n")
        file.write(error)
        file.write("\nERROR END\nERROR END\n")

def select(menu, key, pos):
    if key == ord("s"):
        pos += 1
        if pos >= len(menu):
            pos = len(menu) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    screens["source"].addstr(pos - back, 0, menu[pos - back])
    screens["source"].addstr(pos, 0, menu[pos], colors["server"])
    return pos

def update():
    global security, network, users, inp, msg
    while True:
        if pause:
            time.sleep(1)
            continue
        time.sleep(1)
        screens["bar"].addstr(0, width // 2 - (len(security) // 2), security, colors["hl2"])
        screens["bar"].addstr(0, width - width // 3, "              ", colors["hl1"])
        screens["bar"].addstr(0, (width - (width // 4)) - (len(network) // 2), network, colors["hl2"])
        screens["bar"].addstr(0, width // 7, str(len(session_usr)), colors["hl1"])
        screens["bar"].refresh()

def print_text(pos_y, pos_x, msg, color):
    i = 0
    for item in msg:
        screens["chat"].addstr(pos_y + i, pos_x, item, color)
        i += 1
    screens["chat"].refresh()

def clearchk():
    global y
    if y >= height - 7:
        screens["chat"].erase()
        y = 0
        screens["chat"].refresh()

def message_recv():
    global y, msg, users
    x = 0
    while True:
        num = 0
        msg = server.recv(4096)
        if pause:
            time.sleep(1)
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

            for i in msg:
                if i == '\n':
                    num += 1
            clearchk()
            if "server.message.from.server" in msg:
                msg = msg.replace("server.message.from.server", "")
                response, msg = msg.split(".", 1)
                if "users:" in msg:
                    response, msg = msg.split("!")
                    response = response.strip("users:")
                    users += int(response.strip())
                screens["chat"].addstr(y, x, msg, colors["server"])
            else:
                screens["chat"].addstr(y, x, msg, colors["hl3"])
        if num != 1:
            y += num
        clearchk()
        screens["chat"].refresh()

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
    global y
    success = 0
    ref(screens["input"])
    clr()
    screens["chat"].addstr(y, 0, "Users:", colors["hl1"])
    y += 1
    names = os.listdir(curusr+"/.zinapp/phonebook")
    for name in names:
        screens["chat"].addstr(y, 0, name.strip(".txt"), colors["hl1"])
        y += 1
    y += 1
    print_text(y, 0, ("Whos contact would you like to view?",), colors["hl1"])
    inp = screens["text"].edit().strip()
    if inp:
        ref(screens["input"])
        clr(None, screens["chat"], None, None)
        for item in names:
            if inp.lower() == item.strip(".txt").lower() or inp.strip("@").lower() == item.strip(".py").strip("@").lower():
                with open(curusr+f"/.zinapp/phonebook/{item}", "r") as file:
                    data = file.readlines()
                    for item in data:
                        screens["chat"].addstr(y, 0, item, colors["hl1"])
                        y += 1
                y += 1
                print_text(y, 0, ("Press enter to continue",), colors["hl1"])
                success = 1
                inp = screens["text"].edit().strip()
                if inp:
                    ref(screens["input"])
    if not success:
        print_text(y + 1, 0, ("User does not exist",), colors["hl1"])
        time.sleep(1)
    
    clr(None, screens["chat"], None, None)

def savenick():
    global pause, y
    if not session_usr:
        return
    success = 0
    pause = 1
    data = []

    ref(screens["input"])
    ref(screens["chat"])
    y = 2
    print_text(y, 0, ("Who would you like to add to your contacts?",), colors["hl1"])
    y += 1
    inp = dynamic_inps(session_usr, y)
    data.append(inp.strip("@"))
    if inp:
        clr()        
        print_text(y, 0, ("Next we will fill out extra information about the user.\nNickname:",), colors["hl1"])
        inp = get_input()
        if inp:
            data.append(inp)
        clr()
        print_text(y, 0, ("IP Address:",), colors["hl1"])
        inp = get_input()
        if inp:
            data.append(inp)
        clr()
        print_text(y, 0, ("Notes:",), colors["hl1"])
        inp = get_input()
        if inp:
            data.append(inp)
        clr()
        with open(curusr+f"/.zinapp/phonebook/{data[0]}.txt", "w") as file:
            file.write(f"name: {data[0]}\n")
            file.write(f"nickname: {data[1]}\n")
            file.write(f"ip address: {data[2]}\n")
            file.write(f"notes: {data[3]}\n")
            success = 1
    if success:
        msg = "Writing to file, please wait..."
    else:
        msg = "User does not exist. Exiting..."
    print_text(y + 1, 0, (msg,), colors["hl1"])
    time.sleep(1)
    clr()
    pause = 0
    return "User added", 0

def notrase(inp, upd, yplus):
    i = 0
    for char in inp:
        screens["chat"].addstr(y + yplus, i, " ", colors["erase"])
        i += 1
    if upd:
        screens["chat"].refresh()

def batch_erase(text, y_offset):
    i = 0
    for item in text:
        notrase(text, 0, y_offset + i)
        i += 1
    screens["chat"].refresh()

"""user functions"""

def shutoff():
    update_thread.join()
    screens["source"].clear()
    print_text(height // 2, width // 2, ("    exiting...",), colors["hl3"])
    message_thread.join(timeout=1)
    curses.nocbreak()
    screens["source"].keypad(False)
    curses.echo()
    curses.endwin()
    server.close()
    sys.exit()

def listcmd():
    result = ""
    i = 0
    for item in commands:
        result += item + "\n"
        i += 1
    return result, i - 1

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
    return f"autoconnect set to {attr_dict['autoconnect']}", 0

def clr():
    global y
    screens["chat"].clear()
    screens["chat"].refresh()
    y = 0
    return "clear", 0

def ref(screen):
    screen.clear()
    screen.refresh()

def changeuser():
    ref(screens["input"])
    print_text(y + 1, 0, ("What would your username like to be?",), colors["hl1"])
    inp = screens["text"].edit().strip()
    if inp:
        attr_dict["name"] = inp.strip()
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, val in attr_dict.items():
                file.write(f"{title}={val}\n")
    ref(screens["input"])
    notrase("What would your username like to be?", 0, 1)
    print_text(y + 1, 0, ("Writing to file, please wait...",), colors["hl1"])
    time.sleep(1)
    notrase("Username updated!", 0, 1)
    print_text(y + 1, 0, ("Username updated!",), colors["hl1"])
    time.sleep(1)
    notrase("Writing to file, please wait...", 1, 1)
    return "", 0

def set_qkeys():
    with open(""):
        return

def importip():
    global ipid, alias
    ref(screens["input"])
    msg = ("This will assist you in connecting to networks","We will assign an ID to an IP address","please enter the IP address youd like to give an ID")
    print_text(y, 0, msg, colors["hl1"])
    inp = screens["text"].edit().strip()
    if inp:
        attr_dict["idaddr"] = inp.strip()
    ref(screens["input"])
    batch_erase(msg, 1)
    msg = ("For the ID, you can enter any number or text", "You can only have one ID total", "please enter the ID to be assigned")
    print_text(y, 0, msg, colors["hl1"])
    inp = screens["text"].edit().strip()
    if inp:
        attr_dict["alias"] = inp.strip()
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, val in attr_dict.items():
                file.write(f"{title}={val}\n")
    ref(screens["input"])
    batch_erase(msg, 1)
    print_text(y + 1, 0, ("Writing to file, please wait...",), colors["hl1"])
    time.sleep(1)
    notrase("Writing to file, please wait...", 0, 1)
    print_text(y + 1, 0, ("Connection ID added. To skip the connection process entirely, configure #autostart",), colors["hl1"])
    time.sleep(1)
    notrase("Connection ID added. To skip the connection process entirely, configure #autostart", 1, 1)
    return "", 0

commands = {"#help": listcmd, "#exit": shutoff, "#query-user": query, "#add-user": savenick, "#change-user": changeuser, "#autoconnect":auto_conf, "#import-ip":importip, "#clear": clr}

"""init and main functions"""

def group_message():
    global y, pause, threads_started
    while not gc_config_init():
        continue
    if not threads_started:
        screens["bar"].refresh()
        update_thread = task.Thread(target=update)
        message_thread = task.Thread(target=message_recv, daemon=True)
        update_thread.start()
        message_thread.start()
        threads_started = 1
    pause = 0
    x = 0
    while True:
        try:
            inp = screens["text"].edit().strip()
            if inp:
                y += 2
                clearchk()
                if "#" in inp and '"' not in inp:
                    xcute = commands.get(inp)
                    if xcute:
                        result, adjust_y = xcute()
                    else:
                        result = "invalid"
                    clearchk()
                    if result:
                        screens["chat"].addstr(y, x, result, colors["hl4"])
                    if adjust_y:
                        y += adjust_y
                    ref(screens["input"])
                    screens["chat"].refresh()
                    result = None
                    continue
                
                if "server.main." not in inp or '"' in inp:
                    screens["chat"].addstr(y, x, inp, colors["hl4"])
                ref(screens["input"])
                screens["chat"].refresh()
                server.sendall(inp.encode("utf-8"))
                inp = None
        except KeyboardInterrupt:
                server.close()
                exit()
        except Exception as e:
            screens["source"].clear()
            screens["source"].addstr(height // 2, width // 2, str(e))
            screens["source"].refresh()

def direct_message(name):
    global y, pause, threads_started
    x = 0
    while not gc_config_init():
        continue
    if not threads_started:
        screens["bar"].refresh()
        update_thread = task.Thread(target=update)
        message_thread = task.Thread(target=message_recv, daemon=True)
        update_thread.start()
        message_thread.start()
        threads_started = 1
    pause = 0
    while True:
        try:
            inp = screens["text"].edit().strip()
            if inp:
                y += 2
                clearchk()
                screens["chat"].addstr(y, x, inp, colors["hl4"])
                ref(screens["input"])
                screens["chat"].refresh()
                server.sendall(f"@{name}:{inp}".encode("utf-8"))
                inp = None
        except KeyboardInterrupt:
                server.close()
                exit()
        except Exception as e:
            screens["source"].clear()
            screens["source"].addstr(height // 2, width // 2, str(e))
            screens["source"].refresh()


def contact_selection():
    y = 0
    clean_names = []
    names = os.listdir(curusr+"/.zinapp/phonebook")
    if not names:
        return 0
    for name in names:
        screens["chat"].addstr(y, 0, name.strip(".txt"), colors["hl1"])
        clean_names.append(name.strip(".txt"))
        y += 1
    y += 1
    print_text(y, 0, ("Who would you like to message?",), colors["hl1"])
    name = inps(clean_names)
    direct_message(name)

def gc_config_init():
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attr = file.readlines()
        for item in attr:
            if item == "\n":
                pass
            else:
                item, attr = item.split("=")
                attr_dict[item.strip()] = attr.strip()
        if attr_dict["autoconnect"] == "true":
            try:
                autoconnect()
            except netcom.error as e:
                print_text(height // 2, width // 3, ("Connection refused, try again?",), colors["hl3"])
                choice = get_input()
                ref(screens["input"])
                ref(screens["chat"])
                if "y" in choice:
                    return 2
                else:
                    return 0
            except Exception as e:
                print_text(height // 2, width // 2, (f"UNKNOWN EXCEPTION, CHECK LOGS @{conf_path}",), colors["hl3"])
                errlog(str(e))
                return 0
        else:
            manual_conf("false")
        return 1

def manual_conf(state):
    global server
    os.makedirs(conf_path, exist_ok=True)
    ref(screens["input"])
    if state == "true":
        msg = ("It looks like its your first time starting the messenger.", "Lets start by getting the username youd like to use")
        print_text(y + 1, 0, msg, colors["hl1"])
    else:
        pass
    print_text(y + 3, 0, ("please enter your desired username",), colors["hl3"])
    inp = screens["text"].edit().strip()
    if inp:
        attr_dict["name"] = inp.strip()
    ref(screens["input"])
    ref(screens["chat"])
    if state == "true":
        msg = ("Next enter the IP address of the message server your connecting to", "If you are hosting the server yourself, 'localhost' will work")
        print_text(y + 1, 0, msg, colors["hl1"])   
    print_text(y + 3, 0, ("please enter the IP to connect to",), colors["hl3"])
    inp = screens["text"].edit().strip()
    if inp:
        attr_dict["ipaddr"] = inp.strip()
    ref(screens["input"])
    if state == "true":
        print_text(y + 1, 0, ("Writing to file, please wait...",), colors["hl1"])
    ref(screens["chat"])
    print_text(y + 2, 0, ("Attempting connect. To skip the connection process entirely, configure #autostart",), colors["hl1"])
    time.sleep(1)
    notrase("Attempting connect. To skip the connection process entirely, configure #autostart", 1, 2)
    if state == "true":
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, data in attr_dict.items():
                file.write(f"{title}={data}\n")
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"], port))
    server.sendall(attr_dict["name"].encode("utf-8"))
    network = "connected!    "
    msg = ("Connection accepted! Moving to shell..",)
    print_text(y // 2, width // 2 - len(msg), msg, colors["hl3"])
    time.sleep(1)
    ref(screens["chat"])

def autoconnect():
    global server
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attrs = file.readlines()
        for item in attrs:
            title, val = item.split("=")
            attr_dict[title.strip()] = val.strip()
    ref(screens["chat"])
    msg = (f"Connecting to: {attr_dict['idaddr']}", f"Username: {attr_dict['name']}", "Waiting for accept...")
    print_text(y + 1, 0, msg, colors["hl1"])
    time.sleep(1)
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"].strip(), port))
    server.sendall(attr_dict["name"].encode("utf-8"))
    network = "connected!    "
    screens["chat"].clear()
    msg = "Connection accepted! Moving to shell.."
    print_text(y // 2, width // 2 - len(msg), (msg,), colors["hl3"])
    time.sleep(1)
    ref(screens["chat"])
  
wrapper(main)
