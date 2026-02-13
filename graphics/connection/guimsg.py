#!/usr/bin/env python3
main_menu = ["Messenger", "Group Chat", "Contacts", "Settings", "Systems Test", "Exit"]

import subprocess
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

try:
    import pyaudio
    allow_calling = 1
    main_menu.insert(2, "Caller")    
    codes = {"call-start": "001", "call-confirmation": "002", "call-end": "003", "call-timeout": "004", "err": "000"}

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 2048
    audio = pyaudio.PyAudio()

except:
    allow_calling = 0
    print("pyaudio is not installed, calling will be disabled")
    time.sleep(2)


client_version = 5.3

curusr = os.path.expanduser("~")

session_usr = []

conf_path = curusr+ "/.zinapp/ztext"
username = "none"
alias = "none"
autoconn = "false"
mode = "normal"
modes = ["pretty", "normal", "performance", "minimal"]
themes = ["standard", "cool", "sunny", "cloudy", "lava", "water", "hearts", "leaves", "berries_one", "berries_two", "berries_three"]
color_choice = "standard"
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
server = None
qkeys = {}
pause = 0
pause_receiving = 0
receiving = 1
threads_started = 0
file_io = 0
header_size = 10

batter_colors = {}

data_name = ""
data_path = ""

pos = 0
sx = 0
lvl = 0
origin = 0
num = 0

xlimit = 70 #minimum size of screen before forcing CLI
ylimit = 4
cur_dir = os.path.expanduser("~")
files_in_path = os.listdir(cur_dir)
SELECT = None
data = None
hidden = 1

bugs = [
"-------Known Bugs:-------"
" ",
" ",
"When exiting the messenger and restarting the recv thread it wont display",
" ",
"The battery percent only supports devices with one battery due to improper math",
"The file upload messages can overwrite the one on the screen",
"Text hits the bottom of the screen",       
"No compenstation for screen size",
"----Features coming soon:----",
" ",
"New performance modes - half done",
"Emojis",
"In-build simple games",
"Calling",
"More themes - done",
"Custom text box for arrow key usage and saving recent messages",
"Keybings for quick responses"
]

patches = [
f"------{client_version} patches:------",
" ",
"Added seperate colors for battery percents",
"Added CLI mode",
"Uploading now doesnt break CLI",
"Battery percents now work with multiple batteries."
]
attr_dict = {"ipaddr": ip, "name": username, "autoconnect": autoconn, 
"idaddr": ipid, "alias":alias, "mode":mode, "file path":  os.path.expanduser("~"), 
"theme": color_choice, "sample rate":RATE}



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

def center_print_list(ypos, listy):
    i = 0
    for item in listy:
        if "----" in item:
            screens["source"].addstr(ypos + i, width // 2 - (len(item) // 2), item, colors["server"])
        else:
            screens["source"].addstr(ypos + i, width // 2 - (len(item) // 2), item)
        i += 1
    screens["source"].refresh()
    return i

def find_longest_item(listy):
    total = 0
    for item in listy:
        if len(item) > total:
            total = len(item)
    return item

def generate_theme(selection):
    #black, red green, yellow, blue, magenta, cyan, white
    curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)
    if selection == "berries_one":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    elif selection == "berries_two":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
    elif selection == "berries_three":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    elif selection == "hearts":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    elif selection == "leaves":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_GREEN)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_YELLOW)
    elif selection == "standard":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
    elif selection == "cool":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_WHITE)
    elif selection == "sunny":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    elif selection == "cloudy":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    elif selection == "lava":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_WHITE)
    elif selection == "water":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)


    HIGHLIGHT_1 = curses.color_pair(1)
    HIGHLIGHT_2 = curses.color_pair(2)
    HIGHLIGHT_3 = curses.color_pair(3)
    HIGHLIGHT_4 = curses.color_pair(4)
    HIGHLIGHT_5 = curses.color_pair(5)
    FROM_SERVER = curses.color_pair(6)
    BATHIGH = curses.color_pair(7)
    BATNORM = curses.color_pair(8)
    BATLOW = curses.color_pair(9)

    colors.update({"high":BATHIGH})
    colors.update({"norm":BATNORM})
    colors.update({"low":BATLOW})
    colors.update({"hl":HIGHLIGHT_1})
    colors.update({"hl1":HIGHLIGHT_2})
    colors.update({"hl2":HIGHLIGHT_3})
    colors.update({"hl3":HIGHLIGHT_4})
    colors.update({"hl4":HIGHLIGHT_5})
    colors.update({"server":FROM_SERVER})

def main(stdscr):
    global height, width, message_thread, pause
    height, width = stdscr.getmaxyx()
    if width < xlimit:
        attr_dict["mode"] = "minimal"
        save_conf()
        print("screen size is too small, mode changed. restart when ready")
        exit()
    stdscr.clear()
    stdscr.refresh()

    top_win = curses.newwin(0, width, 0, 0)
    show_chat = curses.newwin(height - 3, width, 2, 0)
    user_input = curses.newwin(1, width - 1, height - 2, 1)
    status_win = curses.newwin(1, width - 1, height - 1, 1)

    tbox = Textbox(user_input)
    screens.update({"bar":top_win})
    screens.update({"status":status_win})
    screens.update({"chat":show_chat})
    screens.update({"input":user_input})
    screens.update({"text":tbox})
    screens.update({"source":stdscr})
    
    files_win = curses.newwin(height - 4, width - 1, 2, 0)
    win.update({"main": stdscr, "files": files_win})
    success = 0
    pause = 1
    generate_theme(attr_dict["theme"])
    while True:
        ref(stdscr)
        screens["source"].addstr(0, width // 2 - (len(f"Messenger Version {client_version}") // 2), f"Messenger Version {client_version}")
        screens["chat"].refresh()
        if attr_dict["mode"] != "performance":
            ypos = height // 4
            ypos += center_print_list(ypos, bugs) + 1
            center_print_list(ypos, patches)
        choice = dynamic_inps(main_menu, 2)
        ref(stdscr)
        if choice == "Messenger":
            screens["bar"].refresh()
            if not contact_selection():
                ref(screens["chat"])
                ref(screens["bar"])
                screens["chat"].addstr(5, 0, "No contacts found, add users to your contacts in group chat")
                screens["chat"].addstr(6, 0, "Press any key to continue")
                screens["chat"].refresh()
                screens["chat"].getch()
                continue
        elif choice == "Group Chat":
            group_message()
        elif choice == "Contacts":
            if not contact_edit():
                ref(screens["chat"])
                screens["chat"].addstr(5, 0, "No contacts found, add users to your contacts in group chat")
                screens["chat"].addstr(6, 0, "Press any key to continue")
                screens["chat"].refresh()
                screens["chat"].getch()
            continue
        elif choice == "Settings":
            settings()
        elif choice == "Exit":
            exit()
        elif choice == "Caller":
            call_menu()
        elif choice == "Systems Test":
            diag_menu()

"""menu functions"""
def get_input(prompt=""):
    if attr_dict["mode"] == "minimal":
        if prompt:
            prompt = prompt.strip() + " " #sanitizing input to prevent formatting issues
        return input(prompt+">>> ")
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
    screens["source"].addstr(pos + offset, 0, menu[pos], colors["hl1"])
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
    with open(conf_path+"/err.txt", "w") as file:
        for name, value in attr_dict.items():
            file.write(f"{name}:{value}\n")
        file.write(error)

def log(string):
    i = 0
    name = f"log{i}.txt"
    while name in os.listdir():
        i += 1
        name = f"log{i}.txt"
    with open(name, "w") as file:
        file.write(string)

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

def round_list(list1):
    total = 0
    for item in list1:
        total += item
    return total / len(list1)

def get_batt():
    batteries = []
    sys_path = "/sys/class/power_supply/" 
    for item in os.listdir(sys_path):
        if item.startswith('BAT'):
            battery_path = os.path.join(sys_path, item)
            capacity_file = os.path.join(battery_path, "capacity")
            if os.path.exists(capacity_file):
                try:
                    with open(capacity_file, "r") as file:
                        batteries.append(int(file.read().strip()))
                except (ValueError, IOError):
                    continue
    if batteries:
        return round_list(batteries)
    

    return "N/A"

def update():
    line_erase(len( attr_dict["name"]), 0)
    screens["bar"].addstr(0, 0, attr_dict["name"], colors["hl2"])
    screens["bar"].addstr(0, len(attr_dict["name"]) + 6, f"        " , colors["hl2"])
    if attr_dict['mode'] != "performance":
        battery = str(get_batt())
        if battery != 'N/A':
            if float(battery) < 60:
                color = colors["norm"]
            elif float(battery) < 30:
                color = colors["low"]
            else:
                color = colors["high"]
            screens["bar"].addstr(0, ((width // 2) - (len(battery) // 2) + (len(network) // 2) * 8), battery, color)
        screens["bar"].addstr(0, width - len(f"Users: {str(users)}") - 2, f"Users: {str(users)}", colors["hl2"])
        screens["bar"].addstr(0, len(attr_dict["name"]) + 6, f"Y: {y}" , colors["hl2"])
    screens["bar"].addstr(0, (width // 2) - (len(network) // 2), network, colors["hl2"])

    screens["bar"].refresh()

def line_erase(length, i):
    for _ in range(length):
        screens["bar"].addstr(0, i, " ", colors["hl"])
        i += 1

def print_text(pos_y, pos_x, msg, color=None):

    if not color:
        color = colors["server"]
    i = 0
    for item in msg:
        screens["chat"].addstr(pos_y + i, pos_x, item, color)
        i += 1
    screens["chat"].refresh()

def clearchk(num):
    global y
    if y + num >= height - 4:
        screens["chat"].erase()
        y = 0
        screens["chat"].refresh()

def send(client, data):
    head = str(len(data)).zfill(header_size)
    data = head + data
    client.send(data.encode("utf-8"))

def receive(client):
    data_received = b''
    packet_size = client.recv(header_size).decode("utf-8")
    if not packet_size:
        return 0
    packet_size = int(packet_size)
    while len(data_received) < packet_size:
        data_received += client.recv(packet_size - len(data_received))
    data_received = data_received.decode("utf-8")
    return data_received
        
def autocaps(phrase):
    if "." and " " not in phrase.strip():
        return phrase
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
        screens["chat"].addstr(y + yplus, i, " ", colors["hl"])
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

def listcmd():
    result = ""
    i = 0
    for item in commands:
        result += item + "\n"
        i += 1
    if attr_dict["mode"] == "minimal":
        return result
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
    if attr_dict["mode"] == "minimal":
        return f"autoconnect set to {attr_dict['autoconnect']}"
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
    "Import IP Address":"#import-ip", "Upload Files":"#file", "Settings":"#config", "Exit":"#exit"}
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
    
def print_list_scr(y, x, menu, scr):
    i = 0
    for item in menu:
        scr.addstr(y + i, x, item)
        i += 1
    scr.refresh()
    return i

def add_time(msg):
    if attr_dict["mode"] == "pretty":
        now = datetime.now()
        formatted_time = now.strftime("%H:%M ")
        msg = formatted_time + msg
    return msg

"""main functions"""

missed_messages = []

def tracked_missing(msg):
    global y
    if not msg and missed_messages:
        clearchk(100)
        y += print_list_scr(y, 0, missed_messages, screens["chat"])
        cache = missed_messages
        for item in cache:
            missed_messages.remove(item)
        return
    elif not msg and not missed_messages:
        return
    if msg:
        if "server.message.from.server" in msg:
            msg = msg.replace("server.message.from.server.", "")
            if "users:" in msg:
                response, msg = msg.split("!")
        missed_messages.append(add_time(msg))

def message_recv(server):
    global y, users, threads_started
    x = 0
    recent_message = ""
    time.sleep(0.001) #to make sure to display after the initial refresh
    while receiving:
        num = 0
        msg = receive(server)
        if msg:
            msg = msg.strip()
            if pause:
                tracked_missing(msg)
                continue
            if "@" in msg:
                recvusr, msg = msg.split(":", 1)
                recvusr = recvusr.strip("@").strip()
                if recvusr not in session_usr:
                    session_usr.append(recvusr)
                msg = f"{getnick(recvusr)}{msg}"

            for i in msg:
                if i == '\n':
                    num += 1
            y += 1
            clearchk(num)
            if "server.message.from.server" in msg:
                if attr_dict['mode'] == "performance":
                    continue
                msg = msg.replace("server.message.from.server.", "")
                if "users:" in msg:
                    response, msg = msg.split("!")
                    response = response.replace("users:", "")
                    users = int(response.strip())
                screens["chat"].addstr(y, x, add_time(msg), colors["server"])
            else:
                screens["chat"].addstr(y, x, add_time(msg), colors["hl3"])
            y += num
            update()            
            screens["chat"].refresh()
    threads_started = 0

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
        new_val = None
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
        elif choice == "theme":
            new_val = set_theme()
        elif choice == "sample rate":
            new_val = int(set_rate())
        else:
            print_text(0, 0, (f"{choice}\nCurrent value: {attr_dict[choice]}\nNew value:",),colors["hl1"])
            new_val = get_input()
        if new_val:
            attr_dict[choice] = new_val
            save_conf()
            break
    generate_theme(attr_dict["theme"])
    clr()
    if attr_dict["mode"] == "minimal":
        if server:
            server.shutdown(netcom.SHUT_RDWR)
            server.close()
        print_text(height // 3, width // 2 - (len("You have choosen minimal, the program will now restart to apply changes") // 2), ("You have choosen minimal, the program will now restart to apply changes",))
        screens["chat"].refresh()
        time.sleep(1)
        exit()
    return "New settings applied", 0

def set_rate():
    print_text(0, 0, (f"WARNING: Audio devices depend on the selected sample rate, be careful. If it fails, this program will select a different audio rate.\nCurrent rate: {attr_dict['sample rate']}\nSet rate to:",), colors["hl1"])
    choice = dynamic_inps(["48000", "44100"], 5)
    return choice

def set_mode():
    print_text(0, 0, (f"Current mode:{attr_dict['mode']}\nSet mode to:",), colors["hl1"])
    choice = dynamic_inps(modes, 4)
    return choice

def set_theme():
    print_text(0, 0, (f"Current theme: {attr_dict['theme']}\nSet theme to:",), colors["hl1"])
    choice = dynamic_inps(themes, 4)
    return choice

def group_message():
    global y, pause, threads_started, network, receiving
    network = "Messaging Group"
    server = gc_config_init("g")
    if not server:
        return
    if not threads_started:
        screens["bar"].refresh()
        message_thread = task.Thread(target=message_recv, args=(server,), daemon=True)
        message_thread.start()
        threads_started = 1
    pause = 0
    x = 0
    update()
    running = 1
    while running:
        try:
            inp = screens["text"].edit().strip()
        except KeyboardInterrupt:
            receiving = 0
            server.shutdown(netcom.SHUT_RDWR)
            server.close()
            exit()
        ref(screens["input"])
        if attr_dict['mode'] == "pretty":
            if "." in inp:
                inp = autocaps(inp)
        if inp:
            y += 1
            clearchk(0)
            if inp[0] == "#":
                if inp == "#exit":
                    receiving = 0
                    running = 0
                    y = 0
                    ref(screens["source"])
                    message_thread.join(timeout=1)
                    server.shutdown(netcom.SHUT_RDWR)
                    server.close()
                    return
                adjust_y = None
                xcute = commands.get(inp)
                if xcute:
                    result, adjust_y = xcute()
                else:
                    result = "invalid"
                clearchk(0)
                tracked_missing(None)
                if result:
                    screens["chat"].addstr(y, x, result, colors["hl4"])
                if adjust_y:
                    y += adjust_y
                ref(screens["input"])
                screens["chat"].refresh()
                update()
                time.sleep(0.01)
                pause = 0
                result = None
                continue
            send(server, inp)
            if "server.main." not in inp or '"' in inp:
                screens["chat"].addstr(y, x, add_time(inp), colors["hl4"])
            screens["chat"].refresh()

            inp = None
            if attr_dict['mode'] != "performance":
                update()

def direct_message(name):
    global y, pause, threads_started, network, receiving
    network = f"Messaging {name}"
    server = gc_config_init("d")
    if not server:
        return
    if not threads_started:
        screens["bar"].refresh()
        message_thread = task.Thread(target=message_recv, args=(server,), daemon=True)
        message_thread.start()
        threads_started = 1
    pause = 0
    x = 0
    update()
    while running:
        try:
            inp = screens["text"].edit().strip()
        except KeyboardInterrupt:
            receiving = 0
            server.shutdown(netcom.SHUT_RDWR)
            server.close()
            exit()
        ref(screens["input"])
        if attr_dict['mode'] == "pretty":
            if "." in inp:
                inp = autocaps(inp)
        if inp:
            y += 1
            clearchk(0)
            if inp[0] == "#":
                if inp == "#exit":
                    receiving = 0
                    running = 0
                    y = 0
                    ref(screens["source"])
                    message_thread.join(timeout=1)
                    server.shutdown(netcom.SHUT_RDWR)
                    server.close()
                    return
            send(server, f"@{name}:{inp}")
            if "server.main." not in inp or '"' in inp:
                screens["chat"].addstr(y, x, add_time(inp), colors["hl4"])
            screens["chat"].refresh()

            inp = None
            if attr_dict['mode'] != "performance":
                update()

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
    return name

def diag_menu():
    while True:
        choice = dynamic_inps(["Server test (connection required)", "Audio test", "Direct message test ", "File test (connection required)", "Exit"], 4)
        ref(screens["source"])
        if "Audio" in choice:
            if test_audio():
                print_text(0, 0, ("Test passed! ('enter' to continue)",))
                screens["source"].getch()
        elif "Exit" in choice or not choice:
            return 0
"""server init"""

def gc_config_init(type):
    server = None
    if attr_dict["autoconnect"] == "true":
        try:
            server = autoconnect(type)
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
        server = manual_conf("false", type)
        if not server:
            return 0
    return server

def manual_conf(state, type):
    global users
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
    if type == "c":
        send(server, attr_dict["name"]+"-call")
    else:
        send(server, attr_dict["name"])
    send(server, type)
    if attr_dict["mode"] != "performance":
        ref(screens["chat"])
        msg = ("Connection accepted! Moving to shell..",)
        print_text(height // 3, (width // 2) - (len(msg) // 2), msg, colors["hl3"])
        time.sleep(0.1)
    ref(screens["chat"])
    if type != "c":
        users = int(receive(server))
    return server

def save_conf():
    with open(f"{conf_path}/msg_server.conf", "w") as file:
        for title, data in attr_dict.items():
            file.write(f"{title}={data}\n")

def load_conf():
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attr = file.readlines()
        for item in attr:
            if item == "\n":
                pass
            else:
                item, attr = item.split("=")
                attr_dict[item.strip()] = attr.strip()

def autoconnect(type):
    global users
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
    if type == "c":
        send(server, attr_dict["name"]+"-call")
    else:
        send(server, attr_dict["name"])
    send(server, type)
    if attr_dict["mode"] != "performance":
        ref(screens["chat"])
        msg = "Connection accepted! Moving to shell.."
        print_text(2, 0, (msg,), colors["hl3"])
        time.sleep(0.1)
    if type != "c":
        users = int(receive(server))
    ref(screens["chat"])
    return server
  
"""
Here I am pasting the functions needed to pull up a mock file browser
"""

def find_name(path):
    path = path.rstrip("/")

    if path.startswith("/"):
        path = path[1:]

    parts = path.split("/")
    name = parts[-1]
    parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
    return parent_path, name

def upload():
    global pause, y, file_io
    if file_io:
        return "File operations in progress.", 0
    if attr_dict["mode"] == "performance":
        return upload_performance()
    file_io = 0
    pause = 1
    y = 0
    screens["source"].clear()
    screens["source"].refresh()
    file = netcom.socket(ipv4, tcp)
    file.connect((attr_dict["ipaddr"], port))
    send(file, attr_dict["name"]+"-file")
    send(file, "f")
    choice = dynamic_inps(["Upload", "Download", "Exit"], 2)
    if choice == "Upload":
        while True:
            file_io = 1
            screens["source"].clear()
            screens["source"].refresh()
            path, name = get_file()
            if not path:
                file_io = 0
                screens["source"].clear()
                screens["source"].refresh()
                break
            screens["source"].clear()
            screens["source"].refresh()
            print_text(0, 0, (f"Confirm path?: {path+'/'+name}",), colors["server"])
            choice = dynamic_inps(["Yes", "No"], 4)
            if "N" in choice or not choice:
                file_io = 0
                break
            send(file, f"server.main.send-file")
            send(file, name)
            confirmation = receive(file)
            if confirmation == "server.message.from.server.ALREADY_EXISTS":
                print_text(0, 0, (f"A file with that name already exists, the server will add a number to the end. Continue?",), colors["server"])
                choice = dynamic_inps(["Yes", "No"], 4)
            if "N" in choice or not choice:
                file_io = 0
                break
            file_thread = task.Thread(target=send_file, args=(file, f"{path}/{name}"), daemon=True)
            file_thread.start()
            return "File uploading..", 0
    elif choice == "Download":
        while True:
            file_io = 1
            send(file, "server.main.list-file")
            files = receive(file)
            files = files.strip()
            if files == "server.message.from.server.NO_FILES":
                file.shutdown(netcom.SHUT_RDWR)
                file.close()
                del file
                file_io = 0
                return "No files for download", 0
            file_list = []
            if " " in files:
                for item in files[:]:
                    if item == " ":
                        name, files = files.split(" ", 1)
                        file_list.append(name)
            file_list.append(files)
            screens["source"].clear()
            choice = dynamic_inps(file_list, 0)
            if not choice:
                file_io = 0
                break
            send(file, f"server.main.get-file")
            send(file, choice)
            confirmation = receive(file)
            if confirmation == "server.message.from.server.NOT_FOUND":
                file.shutdown(netcom.SHUT_RDWR)
                file.close()
                del file
                file_io = 0
                return "That file does not exist, check files with 'server.main.file-list'", 0
            file_thread = task.Thread(target=receive_file, args=(file, choice), daemon=True)
            file_thread.start()
            return f"{choice} is downloading..", 0
    file.shutdown(netcom.SHUT_RDWR)
    file.close()
    del file
    return "Exited", 0

def upload_performance():
    global pause, y, file_io
    if file_io:
        return "File operations in progress.", 0
    file_io = 1
    pause = 1
    y = 0
    ref(screens["source"])
    file = netcom.socket(ipv4, tcp)
    file.connect((attr_dict["ipaddr"], port))
    send(file, attr_dict["name"]+"-file")
    send(file, "f")
    choice = dynamic_inps(["Upload", "Download", "Exit"], 2)
    ref(screens["source"])
    if choice == "Upload":
        while True:
            print_text(0, 0, ("Enter the full path to file",), colors["server"])
            path = get_input()
            if not path:
                break
            path, name = find_name(path)
            print_text(0, 0, (f"Confirm path? (y/n): {path+'/'+name}",), colors["server"])
            choice = get_input()
            if "n" in choice.lower():
                break
            elif not choice:
                break
            send(file, f"server.main.send-file")
            send(file, name)
            confirmation = receive(file)
            if confirmation == "server.message.from.server.ALREADY_EXISTS":
                print_text(0, 0, (f"A file with that name already exists, the server will add a number to the end. Continue?",), colors["server"])
                choice = get_input()
                if not choice:
                    file_io = 0
                    break
                if "n" in choice.lower():
                    file_io = 0
                    break
            file_thread = task.Thread(target=send_file, args=(file, f"{path}/{name}"), daemon=True)
            file_thread.start()
            return "File uploading..", 0
    elif choice == "Download":
        while True:
            send(file, "server.main.list-file")
            files = receive(file)
            files = files.strip()
            if files == "server.message.from.server.NO_FILES":
                file.shutdown(netcom.SHUT_RDWR)
                file.close()
                del file
                file_io = 0
                return "No files for download", 0
            file_list = []
            if " " in files:
                for item in files[:]:
                    if item == " ":
                        name, files = files.split(" ", 1)
                        file_list.append(name)
            file_list.append(files)
            while True:
                screens["source"].clear()
                print_text(2, 0, ("Select a file from the provided list",))
                print_list(3, 0, file_list)
                choice = get_input()
                if not choice:
                    file.shutdown(netcom.SHUT_RDWR)
                    file.close()
                    del file
                    file_io = 0
                    return "Exited", 0
                for item in file_list:
                    if choice in item:
                        choice = item
                print_text(0, 0, (f"Confirm file selection: {choice}",), colors["server"])
                choice = get_input()
                if "y" in choice.lower():
                    break
            send(file, f"server.main.get-file")
            send(file, choice)
            confirmation = receive(file)
            if confirmation == "server.message.from.server.NOT_FOUND":
                file.shutdown(netcom.SHUT_RDWR)
                file.close()
                del file
                file_io = 0
                return "That file does not exist, check files with 'server.main.file-list'", 0
            file_thread = task.Thread(target=receive_file, args=(file, choice), daemon=True)
            file_thread.start()
            return f"{choice} downloading..", 0
    file.shutdown(netcom.SHUT_RDWR)
    file.close()
    del file
    return "Exited", 0

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

def send_file(client, name):
    global file_io, y
    last_filled_width = -1
    try:
        file_size = os.path.getsize(name)
        head = str(file_size).zfill(header_size)
        client.send(head.encode("utf-8"))
        sent_bytes = 0
        with open(name, "rb") as file:
            while sent_bytes < file_size:
                chunk = file.read(4096)
                if not chunk:
                    break
                client.send(chunk)
                sent_bytes += len(chunk)
                
                if attr_dict["mode"] == "minimal":
                    pass
                elif attr_dict["mode"] == "performance":
                    progress_percent = (sent_bytes / file_size) * 100
                    progress_mb = sent_bytes / (1024 * 1024)
                    total_mb = file_size / (1024 * 1024)
                    status_msg = f"Uploading: {progress_percent:.1f}% ({progress_mb:.2f}/{total_mb:.2f} MB)"
                    screens["status"].clear()
                    screens["status"].addstr(0, 0, status_msg)
                    screens["status"].refresh()
                else:
                    progress_percent = (sent_bytes / file_size)
                    bar_width = width - 2 
                    filled_width = int(bar_width * progress_percent)
                    if filled_width % max(1, bar_width // 10) == 0:
                        screens["status"].clear()
                        progress_bar = "█" * filled_width
                        screens["status"].addstr(0, 0, progress_bar)
                        screens["status"].refresh()
                        last_filled_width = filled_width
        if attr_dict["mode"] != "minimal":
            time.sleep(0.3)
            screens["status"].clear()
            time.sleep(0.1)
            screens["status"].addstr(0, 0, "Upload complete")
            screens["status"].refresh()
        else:
            print("Upload complete")
        file_io = 0
        return 1
    except (BrokenPipeError, ConnectionResetError, OSError):
        if attr_dict["mode"] != "minimal":
            screens["status"].clear()
            screens["status"].addstr(0, 0, "Upload failed")
            screens["status"].refresh()
        else:
            print("Upload failed")
        return 0

def receive_file(client, name):
    global y, file_io
    last_filled_width = -1
    try:
        data_received = b''
        packet_size = client.recv(header_size).decode("utf-8")
        if not packet_size:
            client_end(client)
            return 0
        packet_size = int(packet_size)
        file_path = attr_dict["file path"]
        
        with open(attr_dict["file path"] + "/" + name, "wb") as file:
            while len(data_received) < packet_size:
                chunk = client.recv(min(4096, packet_size - len(data_received)))
                if not chunk:
                    break
                file.write(chunk)
                data_received += chunk
                
                if attr_dict["mode"] == "minimal":
                    pass
                elif attr_dict["mode"] == "performance":
                    progress_percent = (len(data_received) / packet_size) * 100
                    progress_mb = len(data_received) / (1024 * 1024)
                    total_mb = packet_size / (1024 * 1024)
                    status_msg = f"Downloading: {progress_percent:.1f}% ({progress_mb:.2f}/{total_mb:.2f} MB)"
                    screens["status"].clear()
                    screens["status"].addstr(0, 0, status_msg)
                    screens["status"].refresh()
                else:
                    progress_percent = (len(data_received) / packet_size)
                    bar_width = width - 2 
                    filled_width = int(bar_width * progress_percent)
                    
                    if filled_width != last_filled_width and filled_width % max(1, bar_width // 10) == 0:
                        screens["status"].clear()
                        progress_bar = "█" * filled_width
                        screens["status"].addstr(0, 0, progress_bar)
                        screens["status"].refresh()
                        last_filled_width = filled_width
        if attr_dict["mode"] != "minimal":
            time.sleep(0.1)
            screens["status"].clear()
            time.sleep(0.1)
            screens["status"].addstr(0, 0, "Download complete")
            screens["status"].refresh()
        
        file_io = 0
        return 1
    except (OSError):
        if attr_dict["mode"] != "minimal":
            screens["status"].clear()
            screens["status"].addstr(0, 0, "Download failed")
            screens["status"].refresh()
        else:
            print("Download failed")
        return 0

commands = {"#menu":command_menu, "#help": listcmd, "#query-user": query, 
"#add-user": savenick, "#change-user": changeuser, "#autoconnect":auto_conf, 
"#import-ip":importip, "#clear": clr, "#file": upload, "#config":settings}

"""All of these functions are remakes for CLI"""
#converted functions here
#some functions that are small enough have conditions for CLI
def cli_print_list(menu):
    for item in menu:
        print(item)

def cli_upload():
    global pause, file_io
    if file_io:
        return "File operations in progress."
    file_io = 0
    pause = 1
    file = netcom.socket(ipv4, tcp)
    file.connect((attr_dict["ipaddr"], port))
    send(file, attr_dict["name"]+"-file")
    send(file, "f")
    choice = cli_menu(["Upload", "Download", "Exit"])
    if choice == "Upload":
        while True:
            file_io = 1
            print("Enter the full path to file")
            path = get_input()
            if not path:
                break
            path, name = find_name(path)
            print_text(f"Confirm path?: {path+'/'+name}")
            choice = cli_menu(["Yes", "No"])
            if "N" in choice:
                break
            send(file, f"server.main.send-file")
            send(file, name)
            confirmation = receive(file)
            if confirmation == "server.message.from.server.ALREADY_EXISTS":
                print_text(f"A file with that name already exists, the server will add a number to the end. Continue?")
                choice = cli_menu(["Yes", "No"])
            if "N" in choice:
                break
            file_thread = task.Thread(target=send_file, args=(file, f"{path}/{name}"), daemon=True)
            file_thread.start()
            return "File uploading.."
    elif choice == "Download":
        while True:
            file_io = 1
            send(file, "server.main.list-file")
            files = receive(file)
            files = files.strip()
            if files == "server.message.from.server.NO_FILES":
                file.shutdown(netcom.SHUT_RDWR)
                file.close()
                del file
                file_io = 0
                return "No files for download"
            file_list = []
            if " " in files:
                for item in files[:]:
                    if item == " ":
                        name, files = files.split(" ", 1)
                        file_list.append(name)
            file_list.append(files)
            choice = cli_menu(file_list)
            send(file, f"server.main.get-file")
            send(file, choice)
            confirmation = receive(file)
            if confirmation == "server.message.from.server.NOT_FOUND":
                file.shutdown(netcom.SHUT_RDWR)
                file.close()
                del file
                file_io = 0
                return "That file does not exist, check files with 'server.main.file-list'"
            file_thread = task.Thread(target=receive_file, args=(file, choice), daemon=True)
            file_thread.start()
            return f"{choice} is downloading.."
    file.shutdown(netcom.SHUT_RDWR)
    file.close()
    del file
    return "Exited"

def cli_tracked_missing(msg):
    if not msg and missed_messages:
        cli_print_list(missed_messages)
        cache = missed_messages
        for item in cache:
            missed_messages.remove(item)
        return
    elif not msg and not missed_messages:
        return
    if msg:
        if "server.message.from.server" in msg:
            msg = msg.replace("server.message.from.server.", "")
            if "users:" in msg:
                response, msg = msg.split("!")
        missed_messages.append(add_time(msg))

def cli_message_recv():
    global msg, users, pause, threads_started
    recent_message = ""
    while receiving:
        msg = receive(server)
        if msg:
            msg = msg.strip()
            if pause:
                cli_tracked_missing(msg)
                continue
            if "@" in msg:
                recvusr, msg = msg.split(":", 1)
                recvusr = recvusr.strip("@").strip()
                if recvusr not in session_usr:
                    session_usr.append(recvusr)
                msg = f"{getnick(recvusr)}{msg}"
            if "server.message.from.server" in msg:
                msg = msg.replace("server.message.from.server.", "")
                if "users:" in msg:
                    response, msg = msg.split("!")
                    response = response.replace("users:", "")
                    users = int(response.strip())
            print(msg)
            print(">>> \0")
    threads_started = 0

def cli_settings():
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attrs = file.readlines()
        for item in attrs:
            title, val = item.split("=")
            attr_dict[title.strip()] = val.strip()
    while True:
        new_val = None
        item_list = []
        for item, value in attr_dict.items():
            item_list.append(item)
        choice = cli_menu(item_list)
        if not choice:
            break
        if choice == "mode":
            new_val = cli_set_mode()   
        else:
            print(f"{choice}\nCurrent value: {attr_dict[choice]}\nNew value:")
            new_val = get_input()
        if new_val:
            attr_dict[choice] = new_val
            save_conf()
            break
    if attr_dict["mode"] != "minimal":
        print("Youve chosen to exit minimal, the program will now restart to apply changes")
        if server:
            server.shutdown(netcom.SHUT_RDWR)
            server.close()
        print("Exited.")
        exit()
    return "New settings applied", 0

def cli_set_mode():
    while True:
        print(f"Current mode:{attr_dict['mode']}\nSet mode to:")
        choice = cli_menu(modes)
        return choice

def cli_group_message():
    global pause, threads_started, receiving
    if not cli_gc_config_init("g"):
        return
    if not threads_started:
        message_thread = task.Thread(target=cli_message_recv, daemon=True)
        message_thread.start()
        threads_started = 1
    pause = 0
    x = 0
    running = 1
    while running:
        try:
            inp = get_input()
        except KeyboardInterrupt:
            receiving = 0
            server.shutdown(netcom.SHUT_RDWR)
            server.close()
            exit()
        if inp:
            if inp[0] == "#":
                if inp == "#exit":
                    receiving = 0
                    running = 0
                    y = 0
                    message_thread.join(timeout=1)
                    server.shutdown(netcom.SHUT_RDWR)
                    server.close()
                    return
                xcute = cli_commands.get(inp)
                if xcute:
                    result = xcute()
                else:
                    result = "invalid"
                tracked_missing(None)
                if result:
                    print(result)
                pause = 0
                result = None
                continue
            send(server, inp)
            inp = None

def cli_direct_message():
    global y, pause, threads_started, network, receiving
    name = cli_contact_selection()
    if not name:
        print("No contacts found, add users to your contacts in group chat")
        return
    if not cli_gc_config_init("d"):
        return
    if not threads_started:
        message_thread = task.Thread(target=cli_message_recv, daemon=True)
        message_thread.start()
        threads_started = 1
    pause = 0
    x = 0
    while running:
        try:
            inp = get_input()
        except KeyboardInterrupt:
            receiving = 0
            server.shutdown(netcom.SHUT_RDWR)
            server.close()
            exit()
        if inp:
            if inp[0] == "#":
                if inp == "#exit":
                    receiving = 0
                    running = 0
                    y = 0
                    message_thread.join(timeout=1)
                    server.shutdown(netcom.SHUT_RDWR)
                    server.close()
                    return
            send(server, f"@{name}:{inp}")
            if "server.main." not in inp or '"' in inp:
                print(add_time(inp))
            inp = None

def cli_gc_config_init(type):
    if attr_dict["autoconnect"] == "true":
        try:
            cli_autoconnect(type)
        except netcom.error as e:
            print("Connection refused, try again?")
            choice = cli_menu(["Yes", "No"])
            if "Y" in choice:
                return 2
            else:
                return 0
        except Exception as e:
            print(f"UNKNOWN EXCEPTION, CHECK LOGS @{conf_path}")
            errlog(str(e))
            return 0
    else:
        if not cli_manual_conf("false", type):
            return 0
    return 1

def cli_contact_selection():
    clean_names = []
    names = os.listdir(curusr+"/.zinapp/phonebook")
    if not names:
        return 0
    for name in names:
        clean_names.append(name.strip(".txt"))
    print("Who would you like to message?")
    y += 3
    name = menu(clean_names)
    if not name:
        return
    direct_message(name)

def cli_manual_conf(state, type):
    global server, users
    os.makedirs(conf_path, exist_ok=True)
    if state == "true":
        print("It looks like its your first time starting the messenger.\nLets start by getting the username youd like to use")
    else:
        pass
    print("please enter your desired username")
    inp = get_input()
    if not inp:
        return
    attr_dict["name"] = inp.strip()
    if state == "true":
       print("Next enter the IP address of the message server your connecting to\nIf you are hosting the server yourself, 'localhost' will work")
    print("please enter the IP to connect to")
    inp = get_input()
    if not inp:
        return
    attr_dict["ipaddr"] = inp.strip()
    if state == "true":
        print("Writing to file, please wait...")
    print("Attempting connect. To skip the connection process entirely, configure #autostart")
    time.sleep(0.1)
    save_conf()
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"], port))
    send(server, attr_dict["name"])
    send(server, type)
    print("Connection accepted! Moving to shell..")
    time.sleep(0.1)
    users = int(receive(server))
    return 1

def cli_autoconnect(type):
    global server, users
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attrs = file.readlines()
        for item in attrs:
            title, val = item.split("=")
            attr_dict[title.strip()] = val.strip()
    print(f"Connecting to: {attr_dict['idaddr']}\nUsername: {attr_dict['name']}\nWaiting for accept...")
    time.sleep(0.1)
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"].strip(), port))
    send(server, attr_dict["name"])
    send(server, type)
    print("Connection accepted! Moving to shell..")
    time.sleep(0.1)
    users = int(receive(server))
  
#new CLI only functions here

def cli_battery():
    print(get_batt())

def cli_bugs():
    for item in bugs:
        print(item)

def cli_patches():
    for item in patches:
        print(item)

def cli_menu(menu=None): #lists only
    while True:
        cli_print_list(menu)
        choice = get_input()
        if not choice:
            return
        for item in menu:
            if choice.lower() in item.lower():
                choice = item
                return choice
        print("Invalid option")

def start():
    print(f"Client Version {client_version}")
    while True:
        menu = {"Direct Message":cli_direct_message,"Group Message":cli_group_message, "Patches":cli_patches, "Bugs":cli_bugs, "Settings":cli_settings, "Exit":exit}
        choice = cli_menu(["Direct Message","Group Message","Patches","Bugs","Settings","Exit"])
        if not choice:
            exit() 
        xcute = menu.get(choice)
        if xcute:
            print("\n###################")
            xcute()
            print("###################\n")
            continue
        print("Invalid option")

cli_commands = {"#help": listcmd, "#autoconnect":auto_conf, "#file": cli_upload, "#config":cli_settings, "#batt":cli_battery}


"""calling functions""" #some bugs exist when calling so ill note -

#the solution to stopping the call without adding another thread connection is to send empty data and then the end flag
#this way the server wont end the thread just on empty data and a recv timeout will also solve ctrl-c
#just have the server expect the end flag on empty data only

"""local conf"""
print("\n\n")
curusr = os.path.expanduser("~")
call_conf_path = curusr + "/.zinapp/call"
if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "call" not in os.listdir(curusr + "/.zinapp"):
    os.mkdir(call_conf_path)

def test_audio():
    global live, in_devices, out_devices, audio_in, audio_out
    ref(screens["source"])
    audio_in, audio_out, in_devices, out_devices = discover()
    screens["source"].addstr(0, width - (len(f"Input device: {current_in} | Output device: {current_out}") + 1), f"Input device: {current_in} | Output device: {current_out}",)
    print_text(1, 0, ("Currently testing and diagnosing audio. Please select your audio device. 'Enter' to continue",))
    screens["source"].getch()
    audio_in, audio_out, status = audio_config(1)
    ref(screens["source"])
    screens["source"].addstr(0, width - (len(f"Input device: {current_in} | Output device: {current_out}") + 1), f"Input device: {current_in} | Output device: {current_out}",)
    if not status:
        print_text(1, 0, ("Audio init failed with your selected devices. Results have been logged in your current directory",))
        return 0
    print_text(1, 0, ("Starting playback testing.",))
    time.sleep(0.5)
    print_text(0, 3, ("I/O: ",))
    time.sleep(0.3)
    self_test = task.Thread(target=play_self, args=(audio_in, audio_out), daemon=True)
    print_text(0, 3, ("I/O: Thread created",))
    time.sleep(0.3)
    print_text(0, 3, ("I/O: Waiting to start",))
    time.sleep(0.3)
    live = 1
    if self_test:
        try:
            self_test.start()
            failed = False
            print_text(0, 3, ("I/O: Audio thread started!",))
            time.sleep(0.3)
        except Exception as e:
            live = 0
            failed = True
            print_text(0, 3, ("I/O: FAILED: Audio thread has failed. Error logged in current directory",))
            time.sleep(0.7)
            log(str(e))
    if failed:
        ref(screens["source"])
        print_text(0, 0, ("Audio test failed, results logged. returning.",))
        return 0
    print_text(0, 4, ("Testing for 10 seconds.",))
    time.sleep(10)
    live = 0
    ref(screens["source"])
    return 1
    
def call_menu():
    global audio_in, audio_out, in_devices, out_devices, call_server
    ref(screens["source"])
    call_server, in_call = init_to_call()
    if call_server:
        audio_in, audio_out, in_devices, out_devices = discover()
        screens["source"].addstr(0, width - (len(f"Input device: {current_in} | Output device: {current_out}") + 1), f"Input device: {current_in} | Output device: {current_out}")
        call_check_thread = task.Thread(target=listen_for_call, args=(call_server,), daemon=True)
        call_check_thread.start()
 
    while True:
        if call_server:
            screens["bar"].addstr(0, 0, "Connected to Server")
        else:
            screens["bar"].addstr(0, 0, "Not Connected to Server")
        screens["bar"].refresh()
        call_menu = ["Contacts", "Audio Devices", "Exit"]
        choice = dynamic_inps(call_menu, 2)
        if choice == "Contacts":
            name = contact_selection()
            if not name:
                ref(screens["source"])
                screens["source"].addstr(0, 0, f"No name selected or contact list is empty. Press any key to continue")
                screens["source"].getch()
                continue
            ref(screens["source"])
            screens["source"].addstr(1, 0, f"Call {name}?")
            choice = dynamic_inps(["Yes", "No"], 3)
            if "Y" not in choice:
                continue
            calling = True
            live = 1
            live_out = 1
            ref(screens["source"])
            confirm = start_call() 
            ref(screens["source"])
            if confirm == codes["call-confirmation"]: 
                print_text(0, 0, "Call accepted.. Starting audio threads")
                time.sleep(0.5)
                print_text(0, 2, "Input: ")
                print_text(0, 3, "Output: ")
                time.sleep(0.2)
                audin_thread = task.Thread(target=record, args=(call_server, audio_in), daemon=True)
                print_text(0, 2, "Input: Thread created")
                time.sleep(0.2)
                print_text(0, 2, "Input: Waiting to start")
                time.sleep(0.2)
                if audio_in:
                    try:
                        audin_thread.start()
                        print_text(0, 2, "Input: Audio input thread started!")
                    except Exception as e:
                        failed = True
                        print_text(0, 2, "Input: FAILED: Audio input thread has failed. Error logged in current directory")
                        log(str(e))
                audout_thread = task.Thread(target=playback, args=(call_server, audio_out), daemon=True)
                print_text(0, 2, "Output: Thread created")
                time.sleep(0.2)
                print_text(0, 2, "Output: Waiting to start")
                time.sleep(0.2)
                if audio_out:
                    try:
                        audout_thread.start()
                        print_text(0, 2, "Output: Audio input thread started!")
                    except Exception as e:
                        failed = True
                        print_text(0, 2, "Output: FAILED: Audio input thread has failed. Error logged in current directory")
                        log(str(e))
            
            elif confirm == codes["call-timeout"]:
                print("call timed out, user isn't available or connected to the server")
                calling = False
                caller = None  # Reset caller on timeout
                continue
            else:
                print(f"call ended or rejected")
                calling = False
                caller = None  # Reset caller on rejection/end
            

        elif choice == "Audio Devices":
            audio_in, audio_out, status = audio_config()
        else:
            return 0
        ref(screens["source"])

def start_call(call_server, name):
    if not name:
        return codes["call-err"]
    print_text(0, 0, "Starting the call")
    time.sleep(0.2)
    send(call_server, name)
    try:
        confirm = receive(call_server)
        return confirm
    except:
        return codes["call-err"]

def init_to_call():
    try:
        call_server = gc_config_init("c")
    except Exception as e:
        log(str(e))
        return 0, 0
    return call_server, 1

def discover():
    global current_in, current_out
    inlist = []
    indict = {}
    outlist = []
    outdict = {}
    device_in = None
    device_out = None
    
    for i in range(audio.get_device_count()):
        device = audio.get_device_info_by_index(i)
        if device['maxInputChannels'] > 0:
            indict.update({str(i): device['name']})
            inlist.append(str(i))
        if device['maxOutputChannels'] > 0:
            outdict.update({str(i): device['name']})
            outlist.append(str(i))

    if indict:
        current_in = indict[inlist[0]]
        device_in = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, 
                               input_device_index=int(inlist[0]), frames_per_buffer=CHUNK)
    else:
        current_in = "None"
        
    if outdict:
        current_out = outdict[outlist[0]]
        device_out = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, 
                                output_device_index=int(outlist[0]), frames_per_buffer=CHUNK)
    else:
        current_out = "None"
        
    return device_in, device_out, indict, outdict

def listen_for_call(call_server):
    global incoming, caller, shutdown
    while not shutdown:
        try:
            call_attempt = call_server.recv(CHUNK).decode("utf-8")
            if call_attempt and ":" in call_attempt:
                code, caller = call_attempt.split(":", 1)
                if code == codes["call-start"]:
                    incoming = True
                    screens["top"].addstr(0, (width // 2) - (len(f"incoming call from {caller.strip("-call")}") // 2), f"incoming call from {caller.strip("-call")}")                   
        except Exception as e:
            if not shutdown:
                time.sleep(0.5)

def record(call_server, audio_in):
    global live
    try:
        while live:
            audio_buffer = audio_in.read(CHUNK, exception_on_overflow=False)
            send_to_server(audio_buffer)
    except Exception as e:
        pass

def playback(call_server, audio_out):
    global live
    try:
        while live:
            audio_buffer = recv_from_server()
            if not audio_buffer:
                time.sleep(0.01)
                continue
            audio_out.write(audio_buffer)
    except Exception as e:
        live = 0

def play_self(audio_in, audio_out):
    try:
        while live:
            audio_buffer = audio_in.read(CHUNK, exception_on_overflow=False)
            audio_out.write(audio_buffer)
    except Exception as e:
        pass

def shell():
    global live, live_out, audio_in, audio_out, in_devices, out_devices, calling, incoming, caller, stat, shutdown
    stat = "stopped"
    
    while True:
        inp = input(f"\n({stat}) >>> ")
        
        if incoming:
            if inp == "88" or inp == "attempt accept":
                send_to_server(codes["call-confirmation"])
                incoming = False
                calling = True
                live = 1
                live_out = 1
                stat = "running"
                
                audin_thread = task.Thread(target=record, args=(audio_in,), daemon=True)
                audout_thread = task.Thread(target=playback, args=(audio_out,), daemon=True)
                
                if audio_in:
                    try:
                        audin_thread.start()
                    except Exception as e:
                        print(f"FAILED to start input: {e}")
                        
                if audio_out:
                    try:
                        audout_thread.start()
                    except Exception as e:
                        print(f"FAILED to start output: {e}")
                
                # Reset caller after call starts
                caller = None
                continue
                
            elif inp == "00" or inp == "attempt reject":
                send_to_server(codes["call-end"])
                incoming = False
                caller = None  # Reset caller on rejection
                continue

        if "ex" in inp:
            live = 0
            shutdown = True  # Signal threads to stop
            try:
                server.close()  # Close socket connection
            except:
                pass
            print("Shutting down...")
            time.sleep(1)  # Give threads time to exit
            break
            
        elif "restart" in inp:
            live = 0
            time.sleep(0.5)
            live_out = 1
            audio_in, audio_out, in_devices, out_devices = discover()
            print("restarted. try 'start' again")
            stat = "stopped"
            caller = None  # Reset caller on restart
            
        elif "stop" in inp:
            live = 0
            stat = "stopped"
            time.sleep(0.5)
            live_out = 1
            calling = False
            caller = None  # Reset caller when stopping
            
        elif "start" in inp:
            return
                
        else:
            xcute = funcs.get(inp)
            if xcute:
                cachein, cacheout = xcute()
                if cachein and cacheout:
                    audio_in = cachein
                    audio_out = cacheout

def debug():
    print("These are all your usb devices, if your mic is not found it might not be compatible\n")
    try:
        usbs = []
        usbdevs = str(subprocess.run("lsusb", capture_output=True, text=True))
        trash, usbdevs = usbdevs.split("stdout='")
        usbdevs, trash = usbdevs.split("stderr")
        while "\n" in usbdevs:
            dev, usbdevs = usbdevs.split("\n", 1)
            usbs.append(dev)
        usbs.append(usbdevs)
        for item in usbs:
            print(item)
    except:
        print("Could not run lsusb - might not be on Linux")
    return None, None

def audio_config(call_server):
    global current_in, current_out, audio_in, audio_out
    ref(screens["source"])
    if not call_server:
        screens["source"].addstr(0, 0, f"Not connected to server, audio devices not initilized. Press any key to continue")
        screens["source"].getch()
        return
    inpset = 0
    outpset = 0
    screens["source"].addstr(0, 0, f"Input device: {current_in} | Output device: {current_out}")
    
    if in_devices.items():
        names = []
        for index, name in in_devices.items():
            names.append(name)
        screens["source"].addstr(1, 0, "Select input device (q to skip):")
        inp = dynamic_inps(names, 3)
        if inp:
            for index, name in in_devices.items():
                if inp == name:
                    passes = 0
                    inpset = 1
                    current_rate = attr_dict["sample rate"]
                    try:
                        inp = audio.open(format=FORMAT, channels=CHANNELS, rate=current_rate, input=True, 
                                        input_device_index=int(index), frames_per_buffer=CHUNK)
                        break
                    except Exception as e:
                        if passes == 2:
                            log(str(e))
                            return audio_in, audio_out, 0
                        passes += 1
                        if "Invalid sample rate" in str(e):
                            if current_rate == 44100:
                                current_rate = 48000
                            else:
                                current_rate = 44100
                    current_in = in_devices[index]
                    break
    else:
        #print("No input devices to choose, press 'Enter' to continue.")
        screens["source"].getch()
    if out_devices.items():
        screens["source"].clear()
        screens["source"].addstr(0, 0, f"Input changed to {current_in} | Output device: {current_out}")
        names = []
        for index, name in out_devices.items():
            names.append(name)
        screens["source"].addstr(1, 0, "Select output device (q to skip):")
        inp = dynamic_inps(names, 3)
        if inp:
            for index, name in out_devices.items():
                if inp == name:
                    passes = 0
                    outpset = 1
                    current_rate = attr_dict["sample rate"]
                    while True:
                        try:
                            outp = audio.open(format=FORMAT, channels=CHANNELS, rate=current_rate, output=True, 
                                            output_device_index=int(index), frames_per_buffer=CHUNK)
                            break
                        except Exception as e:
                            if passes == 2:
                                log(str(e))
                                return audio_in, audio_out, 0
                            passes += 1
                            if "Invalid sample rate" in str(e):
                                if current_rate == 44100:
                                    current_rate = 48000
                                else:
                                    current_rate = 44100

                    current_out = out_devices[index]
                    
                    break
    else:
        pass
    ref(screens["source"])
    print_text(0, 0, (f"Input changed to {current_in} | Output changed to {current_out} ('enter' to continue)",))
    screens["source"].getch()

        
    if not inpset:
        inp = audio_in
    if not outpset:
        outp = audio_out
    return inp, outp, 1

def get_dev():
    print(f"\ncurrent input: {current_in}\ncurrent_output: {current_out}\n")
    if in_devices.items():
        for index, name in in_devices.items():
            print(name, "<<< input")
    else:
        print("No input devices found. Use 'restart' to rescan")
    if out_devices.items():
        for index, name in out_devices.items():
            print(name, "<<< output")
    else:
        print("No output devices found. Use 'restart' to rescan")
    return None, None

def helpy():
    for key in funcs.keys():
        print(key)
    return None, None

funcs = {"help": helpy, "devices": get_dev, "set device": audio_config, "usb": debug}

"""CLI calling"""

def cli_init_to_server():
    global connected
    try:
        server.connect((server_ip, server_port))
        server.send("REQ".encode("utf-8"))
        reply = server.recv(3).decode("utf-8")
        if reply == "ACK":
            server.send(f"{conf_dict['user']}&{CHUNK}".encode("utf-8"))
            ack = server.recv(3).decode("utf-8")
            if ack == "ACK":
                connected = 1
                call_check_thread = task.Thread(target=listen_for_call, daemon=True)
                call_check_thread.start()
            else:
                print("No ack received, possible sync error")
                connected = 0
        else:
            connected = 0
    except Exception as e:
        print(f"Connection error: {e}")
        connected = 0

def cli_discover():
    global current_in, current_out
    indict = {}
    outdict = {}
    inlist = []
    outlist = []
    device_in = None
    device_out = None
    
    for i in range(audio.get_device_count()):
        device = audio.get_device_info_by_index(i)
        if device['maxInputChannels'] > 0:
            indict.update({str(i): device['name']})
            inlist.append(str(i))
        if device['maxOutputChannels'] > 0:
            outdict.update({str(i): device['name']})
            outlist.append(str(i))

    if indict:
        current_in = indict[inlist[0]]
        device_in = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, 
                               input_device_index=int(inlist[0]), frames_per_buffer=CHUNK)
    else:
        print("no input devices found. Plug one in and retry")
        current_in = "None"
        
    if outdict:
        current_out = outdict[outlist[0]]
        device_out = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, 
                                output_device_index=int(outlist[0]), frames_per_buffer=CHUNK)
    else:
        print("no output devices found. Plug one in and retry")
        current_out = "None"
        
    init_to_server()
    return device_in, device_out, indict, outdict

def cli_listen_for_call():
    """Fixed: Loop continuously instead of breaking after one call"""
    global incoming, caller, shutdown
    while not shutdown:
        try:
            call_attempt = server.recv(CHUNK).decode("utf-8")
            if call_attempt and ":" in call_attempt:
                code, caller = call_attempt.split(":", 1)
                if code == codes["call-start"]:
                    incoming = True
                    print(f"\nincoming call from {caller}\ntype 'attempt accept' or '88' to accept\nto decline, type 'attempt reject' or '00'\n")
                    print(f"({stat if 'stat' in globals() else 'stopped'}) >>> ", end="", flush=True)
                    # Don't break - keep listening for more calls
        except Exception as e:
            if not shutdown:
                time.sleep(0.5)

def cli_send_to_server(data):
    try:
        if isinstance(data, str):
            server.send(data.encode("utf-8"))
        else:
            server.send(data)
    except:
        pass

def cli_recv_from_server():
    try:
        data = server.recv(CHUNK)
        return data
    except:
        return None

def cli_start_call():
    """Fixed: Reset caller and always ask for user input"""
    global live, calling, caller
    
    # Always ask for user when starting a new call
    to_call = input("who would you like to call? ")
    
    if not to_call:
        print("No user specified")
        return codes["call-end"]
    
    server.send(to_call.encode("utf-8"))
    live = 1
    print("sent call request, waiting for response..")
    
    try:
        confirm = server.recv(3).decode("utf-8")
        return confirm
    except:
        return codes["call-end"]

def cli_record(audio_in):
    global live
    try:
        while live:
            audio_buffer = audio_in.read(CHUNK, exception_on_overflow=False)
            send_to_server(audio_buffer)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Record error: {e}")
    finally:
        if audio_in:
            try:
                audio_in.stop_stream()
                audio_in.close()
            except:
                pass

def cli_playback(audio_out):
    global live_out
    try:
        while live:
            audio_buffer = recv_from_server()
            if not audio_buffer:
                time.sleep(0.01)
                continue
            audio_out.write(audio_buffer)
    except Exception as e:
        print(f"Playback error: {e}")
    finally:
        live_out = 0
        if audio_out:
            try:
                audio_out.stop_stream()
                audio_out.close()
            except:
                pass

def cli_shell():
    global live, live_out, audio_in, audio_out, in_devices, out_devices, calling, incoming, caller, stat, shutdown
    audio_in, audio_out, in_devices, out_devices = discover()
    stat = "stopped"
    
    while True:
        inp = input(f"\n({stat}) >>> ")
        
        if incoming:
            if inp == "88" or inp == "attempt accept":
                send_to_server(codes["call-confirmation"])
                incoming = False
                calling = True
                live = 1
                live_out = 1
                stat = "running"
                
                audin_thread = task.Thread(target=record, args=(audio_in,), daemon=True)
                audout_thread = task.Thread(target=playback, args=(audio_out,), daemon=True)
                
                if audio_in:
                    try:
                        audin_thread.start()
                    except Exception as e:
                        print(f"FAILED to start input: {e}")
                        
                if audio_out:
                    try:
                        audout_thread.start()
                    except Exception as e:
                        print(f"FAILED to start output: {e}")
                
                # Reset caller after call starts
                caller = None
                continue
                
            elif inp == "00" or inp == "attempt reject":
                send_to_server(codes["call-end"])
                incoming = False
                caller = None  # Reset caller on rejection
                continue

        if "ex" in inp:
            live = 0
            shutdown = True  # Signal threads to stop
            try:
                server.close()  # Close socket connection
            except:
                pass
            print("Shutting down...")
            time.sleep(1)  # Give threads time to exit
            break
            
        elif "restart" in inp:
            live = 0
            time.sleep(0.5)
            live_out = 1
            audio_in, audio_out, in_devices, out_devices = discover()
            print("restarted. try 'start' again")
            stat = "stopped"
            caller = None  # Reset caller on restart
            
        elif "stop" in inp:
            live = 0
            stat = "stopped"
            time.sleep(0.5)
            live_out = 1
            calling = False
            caller = None  # Reset caller when stopping
            
        elif "start" in inp:
            calling = True
            live = 1
            live_out = 1
            confirm = start_call()
            
            if confirm == codes["call-confirmation"]:
                stat = "running"
                audin_thread = task.Thread(target=record, args=(audio_in,), daemon=True)
                audout_thread = task.Thread(target=playback, args=(audio_out,), daemon=True)
                
                if audio_in:
                    try:
                        audin_thread.start()
                    except Exception as e:
                        print(f"FAILED to start input: {e}")
                        
                if audio_out:
                    try:
                        audout_thread.start()
                    except Exception as e:
                        print(f"FAILED to start output: {e}")
                        
            elif confirm == codes["call-timeout"]:
                print("call timed out, user isn't available or connected to the server")
                calling = False
                caller = None  # Reset caller on timeout
                continue
            else:
                print(f"call ended or rejected")
                calling = False
                caller = None  # Reset caller on rejection/end
                
        else:
            xcute = funcs.get(inp)
            if xcute:
                cachein, cacheout = xcute()
                if cachein and cacheout:
                    audio_in = cachein
                    audio_out = cacheout

def cli_debug():
    print("These are all your usb devices, if your mic is not found it might not be compatible\n")
    try:
        usbs = []
        usbdevs = str(subprocess.run("lsusb", capture_output=True, text=True))
        trash, usbdevs = usbdevs.split("stdout='")
        usbdevs, trash = usbdevs.split("stderr")
        while "\n" in usbdevs:
            dev, usbdevs = usbdevs.split("\n", 1)
            usbs.append(dev)
        usbs.append(usbdevs)
        for item in usbs:
            print(item)
    except:
        print("Could not run lsusb - might not be on Linux")
    return None, None

def cli_audio_config():
    global current_in, current_out, audio_in, audio_out
    inpset = 0
    outpset = 0
    print(f"Input device: {current_in}\nOutput device: {current_out}")
    
    if in_devices.items():
        for index, name in in_devices.items():
            print(f"INPUT {index}. {name}")
        print("Select input device (enter to skip):")
        inp = input("(config INPUT) >>> ")
        if inp:
            for index, name in in_devices.items():
                if int(inp) == int(index):
                    inpset = 1
                    inp = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, 
                                    input_device_index=int(index), frames_per_buffer=CHUNK)
                    current_in = in_devices[index]
                    print(f"INPUT changed to {in_devices[index]}")
                    break
    else:
        print("No input devices to choose, moving to output")

    if out_devices.items():
        for index, name in out_devices.items():
            print(f"OUTPUT {index}. {name}")
        print("Select output device (enter to skip):")
        outp = input("(config OUTPUT) >>> ")
        if outp:
            for index, name in out_devices.items():
                if int(outp) == int(index):
                    outpset = 1
                    outp = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, 
                                     output_device_index=int(index), frames_per_buffer=CHUNK)
                    current_out = out_devices[index]
                    print(f"OUTPUT changed to {out_devices[index]}")
                    break
    else:
        print("No output devices to choose, finalizing")
        
    if not inpset:
        inp = audio_in
    if not outpset:
        outp = audio_out
    return inp, outp

def cli_get_dev():
    print(f"\ncurrent input: {current_in}\ncurrent_output: {current_out}\n")
    if in_devices.items():
        for index, name in in_devices.items():
            print(name, "<<< input")
    else:
        print("No input devices found. Use 'restart' to rescan")
    if out_devices.items():
        for index, name in out_devices.items():
            print(name, "<<< output")
    else:
        print("No output devices found. Use 'restart' to rescan")
    return None, None

def cli_helpy():
    for key in funcs.keys():
        print(key)
    return None, None


load_conf()
if attr_dict["mode"] != "minimal":
    wrapper(main)
else:
    start()
