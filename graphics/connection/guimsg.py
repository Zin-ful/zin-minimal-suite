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
from datetime import datetime
"""
FIX
Change shitty UI to make it more readable
Add file sending
Add "typing..."
Add user information to UI such as name, ip address, etc
Add auto caps & autocorrect
"""

curusr = os.path.expanduser("~")

session_usr = []
conf_path = curusr+ "/.zinapp/ztext"
username = "none"
alias = "none"
autoconn = "false"
mode = "normal"
modes = ["pretty", "normal", "performance"]
running = 1
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
header_size = 10
main_menu = ["Messenger", "Group Chat", "Contacts", "Settings", "Exit"]

attr_dict = {"ipaddr": ip, "name": username, "autoconnect": autoconn, "idaddr": ipid, "alias":alias, "mode":mode}

colors = {}
win = {}
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
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
    HIGHLIGHT = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
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
    show_chat = curses.newwin(height - 3, width, 2, 0)
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    tbox = Textbox(user_input)
    screens.update({"bar":top_win})
    screens.update({"chat":show_chat})
    screens.update({"input":user_input})
    screens.update({"text":tbox})
    screens.update({"source":stdscr})
    
    files_win = curses.newwin(height - 4, width - 1, 2, 0)
    win.update({"main": stdscr, "files": files_win})
    
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
        elif choice == main_menu[1]:
            group_message()
        elif choice == main_menu[2]:
            if not contact_edit():
                ref(screens["chat"])
                screens["chat"].addstr(5, 0, "No contacts found, add users to your contacts in group chat")
                screens["chat"].addstr(6, 0, "Press any key to continue")
                screens["chat"].refresh()
                screens["chat"].getch()
            continue
        elif choice == main_menu[3]:
            settings()
        elif choice == main_menu[4]:
            exit()

"""menu functions"""
def get_input():
    inp = screens["text"].edit().strip()
    ref(screens["input"])
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
        elif inp == ord("q"):
            return 0

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
    return i

def errlog(error):
    if attr_dict['mode'] == "performance":
        return
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
    line_erase(len( attr_dict["name"]), 0)
    screens["bar"].addstr(0, 0, attr_dict["name"], colors["hl2"])
    screens["bar"].addstr(0, len(attr_dict["name"]) + 6, f"        " , colors["hl2"])
    if attr_dict['mode'] != "performance":
        screens["bar"].addstr(0, width - 3, str(len(session_usr)), colors["hl1"])
        screens["bar"].addstr(0, len(attr_dict["name"]) + 6, f"Y: {y}" , colors["hl2"])
    screens["bar"].addstr(0, (width // 2) - (len(network) // 2), network, colors["hl2"])
    screens["bar"].refresh()

def line_erase(length, i):
    for _ in range(length):
        screens["bar"].addstr(0, i, " ", colors["erase"])
        i += 1

def print_text(pos_y, pos_x, msg, color):
    i = 0
    for item in msg:
        screens["chat"].addstr(pos_y + i, pos_x, item, color)
        i += 1
    screens["chat"].refresh()

def clearchk(num):
    global y
    if y + num >= height - 3:
        screens["chat"].erase()
        y = 0
        screens["chat"].refresh()

def send(client, data):
    head = str(len(data)).zfill(header_size)
    data = head + data
    client.send(data.encode("utf-8"))

def receive(client):
    data_received = b''
    packet_size = server.recv(header_size).decode("utf-8")
    packet_size = int(packet_size)
    while len(data_received) < packet_size:
        data_received += server.recv(packet_size - len(data_received))
    data_received = data_received.decode("utf-8")
    return data_received
        
def autocaps(phrase):
    i = 0
    phrase = list(phrase)
    phrase[0] = phrase[0].upper()
    for item in phrase:
        if item == ".":
            i += 1
            while phrase[i] == " ":
                i += 1
            phrase[i] = phrase[i].upper()
            continue
        i += 1
    new_phrase = ""
    for item in phrase:
        new_phrase += item
    return new_phrase

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
    inp = dynamic_inps(session_usr, y + 2)
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
    global running
    running = 0
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

def command_menu():
    global pause, y
    if attr_dict["mode"] == "performance":
        return "Invalid mode setting, prioritizing battery performace.\nYou are not allowed to access the menu under these conditions", 2
    y = 0
    pause = 1
    phrase_to_cmd = {"Help":"#help", "Clear Screen": "#clear", "Query User":"#query-user", 
    "Add User" :"#add-user", "Change Username" :"#change-user", "Toggle Autoconnect":"#autoconnect", 
    "Import IP Address":"#import-ip", "Upload Files":"#file", "Exit":"#exit"}
    phrases = []
    for name, val in phrase_to_cmd.items():
        phrases.append(name)
    ref(screens["source"])
    choice = dynamic_inps(phrases, 2)
    xcute = commands.get(phrase_to_cmd[choice])
    if xcute:
        ref(screens["chat"])
        result, adjust_y = xcute()
    else:
        ref(screens["chat"])
        result = "Command not found for some reason"
        adjust_y = 0
    return result, adjust_y
    
    

"""main functions"""

missed_messages = []

def tracked_missing(msg):
    global y
    if not msg and missed_messages:
        clearchk(100)
        y += print_list(y, x, missed_messages)
        cache = missed_messages
        for item in cache:
            missed_messages.remove(item)
        return
    elif not msg and not missed_messages:
        return
    if msg:
        missed_messages.append(msg)

def message_recv():
    global y, msg, users
    x = 0
    recent_message = ""
    missed_messages = []
    while True:
        num = 0
        msg = receive(server)
        msg = msg.strip()
        if msg:
            if "@" in msg:
                if pause:
                    tracked_missing(msg)
                    continue
                recvusr, msg = msg.split(":", 1)
                recvusr = recvusr.strip("@").strip()
                if recvusr not in session_usr:
                    session_usr.append(recvusr)
                msg = f"{getnick(recvusr)}{msg}"

            for i in msg:
                if i == '\n':
                    num += 1
            clearchk(num)
            
            if "server.message.from.server" in msg:
                if attr_dict['mode'] == "performance":
                    continue
                msg = msg.replace("server.message.from.server", "")
                response, msg = msg.split(".", 1)
                if "users:" in msg:
                    response, msg = msg.split("!")
                    response = response.strip("users:")
                    users += int(response.strip())
                screens["chat"].addstr(y, x, msg, colors["server"])
            else:
                screens["chat"].addstr(y, x, msg, colors["hl3"])
            y += num
            update()            
            screens["chat"].refresh()


def contact_edit():
    y = 1
    clean_names = []
    names = os.listdir(curusr+"/.zinapp/phonebook")
    for name in names:
        clean_names.append(name.strip(".txt"))
        
    menu = ["Add Contact", "Edit Contact", "Remove Contact"]
    choice = dynamic_inps(menu, 2)
    clr()
    if not choice:
        return 1
    
    if choice == menu[0]:
        success = 0
        data = []
        print_text(y, 0, ("Type in the name of your new contact",), colors["hl1"])
        inp = get_input()
        data.append(inp)
        if inp:
            clr()        
            print_text(1, 0, ("Nickname:",), colors["hl1"])
            inp = get_input()
            if inp:
                data.append(inp)
            else:
                data.append(inp)
            clr()
            print_text(1, 0, ("IP Address:",), colors["hl1"])
            inp = get_input()
            if inp:
                data.append(inp)
            else:
                data.append("none")
            clr()
            print_text(1, 0, ("Notes:",), colors["hl1"])
            inp = get_input()
            if inp:
                data.append(inp)
            else:
                data.append("none")
            clr()
            with open(curusr+f"/.zinapp/phonebook/{data[0]}.txt", "w") as file:
                file.write(f"name: {data[0]}\n")
                file.write(f"nickname: {data[1]}\n")
                file.write(f"ip address: {data[2]}\n")
                file.write(f"notes: {data[3]}\n")
                success = 1
        else:
            return 0
        if success:
            msg = "Writing to file, please wait..."
        else:
            msg = "User does not exist. Exiting..."
        print_text(1, 0, (msg,), colors["hl1"])
        time.sleep(0.5)
        clr()
        return 1
    elif choice == menu[1]:
        if not names:
            return 0
        y = 1
        print_text(y, 0, ("Who's contact would you like to edit?",), colors["hl1"])
        y += 3
        name = dynamic_inps(clean_names, y)
        if not name:
            return 0
        with open(curusr+f"/.zinapp/phonebook/{name}.txt", "r") as file:
            data = file.readlines()
        contact_info = {}
        titles = []
        for item in data:
            title, val = item.split(": ")
            titles.append(title.strip())
            contact_info.update({title.strip(): val.strip()})
        clr()
        y = 1
        print_text(y, 0, ("Select the value to update",), colors["hl1"])
        y += 3
        title = dynamic_inps(titles, y)
        if not title:
            return 0
        clr()
        print_text(1, 0, (f"Old Value: {contact_info[title]}\nNew Value: ",), colors["hl1"])
        new_value = get_input()
        if not new_value:
            return 0
        if title == titles[0]:
            os.remove(curusr+f"/.zinapp/phonebook/{contact_info[titles[0]]}.txt")
        contact_info[title] = new_value
        
        with open(curusr+f"/.zinapp/phonebook/{contact_info[titles[0]]}.txt", "w") as file:
            file.write(f"name: {contact_info[titles[0]]}\n")
            file.write(f"nickname: {contact_info[titles[1]]}\n")
            file.write(f"ip address: {contact_info[titles[2]]}\n")
            file.write(f"notes: {contact_info[titles[3]]}\n")
            success = 1
        if success:
            msg = "Writing to file, please wait..."
        else:
            msg = "User does not exist. Exiting..."
        print_text(y + 1, 0, (msg,), colors["hl1"])
        time.sleep(0.5)
        clr()
        return 1
    else:
        if not names:
            return 0
        print_text(y, 0, ("Who's contact would you like to remove?",), colors["hl1"])
        y += 3
        name = dynamic_inps(clean_names, y)
        if not name:
            return 1
        print_text(y + 1, 0, ("Contact removed",), colors["hl1"])
        time.sleep(0.5)
        clr()
        os.remove(curusr+f"/.zinapp/phonebook/{name}.txt")
        return 1

def settings():
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attrs = file.readlines()
        for item in attrs:
            title, val = item.split("=")
            attr_dict[title.strip()] = val.strip()
    while True:
        ref(screens["source"])
        item_list = []
        for item, value in attr_dict.items():
            item_list.append(item)
        choice = dynamic_inps(item_list, 2)
        if not choice:
            break
        clr()
        if choice == "mode":
            new_val = set_mode()        
        else:
            print_text(0, 0, (f"{choice}\nCurrent value: {attr_dict[choice]}\nNew value:",),colors["hl1"])
            new_val = get_input()
        if new_val:
            attr_dict[choice] = new_val
            save_conf()
            break
    clr()

def set_mode():
    while True:
        print_text(0, 0, (f"Current_mode:{attr_dict['mode']}\nSet mode to:",),colors["hl1"])
        choice = dynamic_inps(modes, 4)
        return choice
    
def group_message():
    global y, pause, threads_started, network
    network = "Messaging Group"
    if not gc_config_init("g"):
        return
    if not threads_started:
        screens["bar"].refresh()
        message_thread = task.Thread(target=message_recv, daemon=True)
        message_thread.start()
        threads_started = 1
    pause = 0
    x = 0
    update()
    while running:
        try:
            inp = screens["text"].edit().strip()   
            ref(screens["input"])
            if attr_dict['mode'] == "pretty":
                if "." in inp:
                    inp = autocaps(inp)
            if inp:
                y += 1
                clearchk(0)
                if inp[0] == "#":
                    adjust_y = None
                    xcute = commands.get(inp)
                    if xcute:
                        result, adjust_y = xcute()
                    else:
                        result = "invalid"
                    clearchk(0)
                    if result:
                        screens["chat"].addstr(y, x, result, colors["hl4"])
                    if adjust_y:
                        y += adjust_y
                    ref(screens["input"])
                    screens["chat"].refresh()
                    update()
                    pause = 0
                    result = None
                    continue
                
                if "server.main." not in inp or '"' in inp:
                    screens["chat"].addstr(y, x, inp, colors["hl4"])
                else:
                    inp = None
                    continue
                screens["chat"].refresh()
                send(server, inp)
                inp = None
                if attr_dict['mode'] != "performance":
                    update()
        except KeyboardInterrupt:
                server.close()
                exit()
        except Exception as e:
            screens["source"].clear()
            screens["source"].addstr(height // 2, width // 2 - (len(str(e)) // 2), str(e))
            screens["source"].refresh()

def direct_message(name):
    global y, pause, threads_started, network
    network = f"Messaging {name}"
    x = 0
    while not gc_config_init("d"):
        continue
    if not threads_started:
        screens["bar"].refresh()
        message_thread = task.Thread(target=message_recv, daemon=True)
        message_thread.start()
        threads_started = 1
    pause = 0
    update()
    while True:
        try:
            inp = screens["text"].edit().strip()
            if attr_dict['mode'] == "pretty":
                if "." in inp:
                    inp = autocaps(inp)
            
            if inp:
                y += 2
                clearchk(0)
                screens["chat"].addstr(y, x, inp, colors["hl4"])
                ref(screens["input"])
                screens["chat"].refresh()
                send(server, f"@{name}:{inp}")
                inp = None
                update()
        except KeyboardInterrupt:
                server.close()
                exit()
        except Exception as e:
            screens["source"].clear()
            screens["source"].addstr(height // 2, width // 2, str(e))
            screens["source"].refresh()

def contact_selection():
    y = 1
    clean_names = []
    names = os.listdir(curusr+"/.zinapp/phonebook")
    if not names:
        return 0
    for name in names:
        clean_names.append(name.strip(".txt"))
    print_text(y, 0, ("Who would you like to message?",), colors["hl1"])
    y += 3
    name = dynamic_inps(clean_names, y)
    direct_message(name)


"""server init"""

def gc_config_init(type):
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
                autoconnect(type)
            except netcom.error as e:
                print_text(height // 2, width // 3, ("Connection refused, try again?",), colors["hl3"])
                choice = screens["chat"].getch()
                if choice == ord("y"):
                    return 2
                else:
                    return 0
            except Exception as e:
                print_text(height // 2, width // 2, (f"UNKNOWN EXCEPTION, CHECK LOGS @{conf_path}",), colors["hl3"])
                errlog(str(e))
                return 0
        else:
            if not manual_conf("false", type):
                return 0
        return 1

def manual_conf(state, type):
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
    if not inp:
        return
    attr_dict["name"] = inp.strip()
    ref(screens["input"])
    ref(screens["chat"])
    if state == "true":
        msg = ("Next enter the IP address of the message server your connecting to", "If you are hosting the server yourself, 'localhost' will work")
        print_text(y + 1, 0, msg, colors["hl1"])   
    print_text(y + 3, 0, ("please enter the IP to connect to",), colors["hl3"])
    inp = screens["text"].edit().strip()
    if not inp:
        return
    attr_dict["ipaddr"] = inp.strip()
    ref(screens["input"])
    if state == "true":
        print_text(y + 1, 0, ("Writing to file, please wait...",), colors["hl1"])
    ref(screens["chat"])
    if attr_dict["mode"] != "performance":
        msg = ("Attempting connect. To skip the connection process entirely, configure #autostart",)
        print_text(height // 3, (width // 2) - (len(msg) // 2), msg, colors["hl1"])
        time.sleep(0.1)
        ref(screens["chat"])
    save_conf()
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"], port))
    send(server, attr_dict["name"])
    send(server, type)
    if attr_dict["mode"] != "performance":
        ref(screens["chat"])
        msg = ("Connection accepted! Moving to shell..",)
        print_text(height // 3, (width // 2) - (len(msg) // 2), msg, colors["hl3"])
        time.sleep(0.1)
    ref(screens["chat"])
    return 1

def save_conf():
    with open(f"{conf_path}/msg_server.conf", "w") as file:
        for title, data in attr_dict.items():
            file.write(f"{title}={data}\n")

def autoconnect(type):
    global server
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attrs = file.readlines()
        for item in attrs:
            title, val = item.split("=")
            attr_dict[title.strip()] = val.strip()
    if attr_dict["mode"] != "performance":
        ref(screens["chat"])
        msg = (f"Connecting to: {attr_dict['idaddr']}", f"Username: {attr_dict['name']}", "Waiting for accept...")
        print_text(y + 1, 0, msg, colors["hl1"])
        time.sleep(0.1)
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"].strip(), port))
    send(server, attr_dict["name"])
    send(server, type)
    if attr_dict["mode"] != "performance":
        ref(screens["chat"])
        msg = "Connection accepted! Moving to shell.."
        print_text(2, 0, (msg,), colors["hl3"])
        time.sleep(0.1)
    ref(screens["chat"])
  
"""
Here I am pasting the functions needed to pull up a mock file browser
"""

data_name = ""
data_path = ""

pos = 0
sx = 0
lvl = 0
origin = 0
num = 0

ylimit = 4
cur_dir = os.path.expanduser("~")
files_in_path = os.listdir(cur_dir)
SELECT = None
data = None
hidden = 1

def find_name(path):
    path = path.rstrip("/")

    if path.startswith("/"):
        path = path[1:]

    parts = path.split("/")
    name = parts[-1]
    parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
    return parent_path, name


def upload():
    global pause, y
    pause = 1
    y = 0
    while True:
        screens["source"].clear()
        screens["source"].refresh()
        if attr_dict["mode"] != "performance":
            path, name = get_file()
            if not path:
                screens["source"].clear()
                screens["source"].refresh()
                return "Exited", 0
        else:
            print_text(0, 0, ("Enter the full path to file",), colors["server"])
            path = get_input()
            if not path:
                return "Exited", 0
            path, name = find_name(path)
        if attr_dict["mode"] != "performance":
            screens["source"].clear()
            screens["source"].refresh()
        print_text(0, 0, (f"Confirm path?: {path+'/'+name}",), colors["server"])
        choice = dynamic_inps(["Yes", "No"], 4)
        if "Y" in choice:
            break
    return "File uploaded!", 0
        
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
            return cur_dir, files_in_path[pos]
        elif key == ord('q'):
            return 0, 0

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

commands = {"#menu":command_menu, "#help": listcmd, "#exit": shutoff, "#query-user": query, 
"#add-user": savenick, "#change-user": changeuser, "#autoconnect":auto_conf, 
"#import-ip":importip, "#clear": clr, "#file": upload}



wrapper(main)
