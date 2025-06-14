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

session_usr = []
conf_path = "/etc/ztext"
username = "none"
alias = "none"
autoconn = "false"
users = 0
ready = 0
ipid = "none"
network = ""
security = ""
port = 45454
ip = ""
msg = ''
y = 0
server = ''
qkeys = {}
pause = 0

attr_dict = {"ipaddr": ip, "name": username, "autoconnect": autoconn, "idaddr": ipid, "alias":alias}

if "phonebook" not in os.listdir("/etc"):
    os.makedirs("/etc/phonebook", exist_ok=True)

def main(stdscr):
    global msg, ERASE, TUT, HIGHLIGHT_1, HIGHLIGHT_2, HIGHLIGHT_3, HIGHLIGHT_4, FROM_SERVER, height, width, network, security, users, message_thread, update_thread
    server = netcom.socket(ipv4, tcp)
    server.connect((ip, port))
    server.sendall(username.encode("utf-8"))
    network = "connected!    "
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

    stdscr.clear()
    stdscr.refresh()
    top_win = curses.newwin(0, width, 0, 0)
    show_chat = curses.newwin(height - 5, width, 2, 0)
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    tbox = Textbox(user_input)
    security = "CHATS ARE NOT ENCRYPTED"
    i = 0
    while i < width:
        top_win.addstr(0, i, " ", HIGHLIGHT)
        i += 1
    config_init(show_chat, user_input, tbox)
    top_win.refresh()
    update_thread = task.Thread(target=update, args=(stdscr, top_win, show_chat, user_input,))
    message_thread = task.Thread(target=message_recv, args=(show_chat,), daemon=True)
    update_thread.start()
    message_thread.start()
    message(tbox, user_input, top_win, show_chat, stdscr)

def update(stdscr, top_win, show_chat, user_input):
    global security, network, users, inp, msg
    while True:
        time.sleep(1)
        top_win.addstr(0, width // 2 - (len(security) // 2), security, HIGHLIGHT_2)
        top_win.addstr(0, width - width // 3, "              ", HIGHLIGHT_1)
        top_win.addstr(0, (width - (width // 4)) - (len(network) // 2), network, HIGHLIGHT_2)
        top_win.addstr(0, width // 7, str(len(session_usr)), HIGHLIGHT_1)
        top_win.refresh()

def clearchk(show_chat):
    global y
    if y >= height - 7:
        show_chat.erase()
        y = 0
        show_chat.refresh()


def message_recv(show_chat):
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

            for i in msg:
                if i == '\n':
                    num += 1
            clearchk(show_chat)
            if "server.message.from.server" in msg:
                msg = msg.replace("server.message.from.server", "")
                response, msg = msg.split(".", 1)
                if "users:" in msg:
                    response, msg = msg.split("!")
                    response = response.strip("users:")
                    users += int(response.strip())
                show_chat.addstr(y, x, msg, FROM_SERVER)
            else:
                show_chat.addstr(y, x, msg, HIGHLIGHT_3)
        if num != 1:
            y += num
        clearchk(show_chat)
        show_chat.refresh()

def getnick(name):
    if "@" in name:
        name = name.strip("@")
    if f"{name}.txt" not in os.listdir("/etc/phonebook"):
        return f"@{name}:"
    with open(f"/etc/phonebook/{name}.txt", "r") as file:
        data = file.readlines()
        for item in data:
            if "nickname:" in item:
                item = item.strip("nickname:").strip()
                return f"@{item}:"
    return f"@{name}:"

def query(stdscr, show_chat, tbox, user_input):
    global y
    success = 0
    user_input.clear()
    user_input.refresh()
    clr(None, show_chat, None, None)
    show_chat.addstr(y, 0, "Users:", HIGHLIGHT_1)
    y += 1
    names = os.listdir("/etc/phonebook")
    for name in names:
        show_chat.addstr(y, 0, name.strip(".txt"), HIGHLIGHT_1)
        y += 1
    y += 1
    show_chat.addstr(y, 0, "Whos contact would you like to view?", HIGHLIGHT_1)
    show_chat.refresh()
    inp = tbox.edit().strip()
    if inp:
        user_input.clear()
        user_input.refresh()
        clr(None, show_chat, None, None)
        for item in names:
            if inp.lower() == item.strip(".txt").lower() or inp.strip("@").lower() == item.strip(".py").strip("@").lower():
                with open(f"/etc/phonebook/{item}", "r") as file:
                    data = file.readlines()
                    for item in data:
                        show_chat.addstr(y, 0, item, HIGHLIGHT_1)
                        y += 1
                y += 1
                show_chat.addstr(y, 0, "Press enter to continue", HIGHLIGHT_1)
                success = 1
                show_chat.refresh()
                inp = tbox.edit().strip()
                if inp:
                    user_input.clear()
                    user_input.refresh()
    if not success:
        show_chat.addstr(y + 1, 0, "User does not exist", HIGHLIGHT_1)
        show_chat.refresh()
        time.sleep(1)
    
    clr(None, show_chat, None, None)
                        
    
    
def savenick(stdscr, show_chat, tbox, user_input):
    global pause, y
    if not session_usr:
        return
    success = 0
    pause = 1
    user_input.clear()
    user_input.refresh()
    clr(None, show_chat, None, None)
    show_chat.addstr(y, 0, "Users:", HIGHLIGHT_1)
    y += 1
    for name in session_usr:
        show_chat.addstr(y, 0, name, HIGHLIGHT_1)
        y += 1
    y += 1
    show_chat.addstr(y, 0, "Who would you like to add to your contacts?", HIGHLIGHT_1)
    show_chat.refresh()
    inp = tbox.edit().strip()
    if inp:
        user_input.clear()
        user_input.refresh()
        clr(None, show_chat, None, None)
        for name in session_usr:
            if inp.lower() == name.lower() or name.strip("@").lower() == inp.strip("@").lower():
                data = []
                show_chat.addstr(y, 0, "Were going to fill out information for this user.", HIGHLIGHT_1)
                y += 1
                show_chat.addstr(y, 0, "Name:", HIGHLIGHT_1)
                show_chat.refresh()
                inp = tbox.edit().strip()
                if inp:
                    if "@" in inp:
                        inp = inp.strip("@")
                    newname = inp
                    data.append(inp)
                clr(None, show_chat, None, None)
                user_input.clear()
                user_input.refresh()
                
                show_chat.addstr(y, 0, "Nickname:", HIGHLIGHT_1)
                show_chat.refresh()
                inp = tbox.edit().strip()
                if inp:
                    data.append(inp)
                clr(None, show_chat, None, None)
                user_input.clear()
                user_input.refresh()
                
                show_chat.addstr(y, 0, "IP Address:", HIGHLIGHT_1)
                show_chat.refresh()
                inp = tbox.edit().strip()
                if inp:
                    data.append(inp)
                clr(None, show_chat, None, None)
                user_input.clear()
                user_input.refresh()
                
                show_chat.addstr(y, 0, "Notes:", HIGHLIGHT_1)
                show_chat.refresh()
                inp = tbox.edit().strip()
                if inp:
                    data.append(inp)
                clr(None, show_chat, None, None)
                user_input.clear()
                user_input.refresh()
                
                with open(f"/etc/phonebook/{newname}.txt", "w") as file:
                    file.write(f"name: {data[0]}\n")
                    file.write(f"nickname: {data[1]}\n")
                    file.write(f"ip address: {data[2]}\n")
                    file.write(f"notes: {data[3]}\n")
                    success = 1
    
    user_input.clear()
    user_input.refresh()
    if success:
        msg = "Writing to file, please wait..."
    else:
        msg = "User does not exist. Exiting..."
    show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    show_chat.refresh()
    time.sleep(1)
    clr(None, show_chat, None, None)
    pause = 0
    

def notrase(show_chat, inp, upd, yplus):
    i = 0
    for char in inp:
        show_chat.addstr(y + yplus, i, " ", ERASE)
        i += 1
    if upd:
        show_chat.refresh()
"""user functions"""

def shutoff(stdscr, arg1, arg2, arg3):
    update_thread.join()
    stdscr.clear()
    stdscr.addstr(height // 2, width // 2, "    exiting...", HIGHLIGHT_3)
    stdscr.refresh()
    message_thread.join(timeout=1)
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    server.close()
    sys.exit()

def listcmd(stdscr, arg1, arg2, arg3):
    res = []
    for i in commands:
        res += i
    return str(res).strip("'").strip("[").strip("]")

def auto_conf(stdscr, arg1, arg2, arg3):
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

def clr(stdscr, show_chat, arg2, arg3):
    global y
    show_chat.clear()
    show_chat.refresh()
    y = 0
    return "clear"

def changeuser(stdscr, show_chat, tbox, user_input):
    user_input.clear()
    user_input.refresh()
    msg = "What would your username like to be?"
    show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    show_chat.refresh()
    inp = tbox.edit().strip()
    if inp:
        attr_dict["name"] = inp.strip()
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, val in attr_dict.items():
                file.write(f"{title}={val}\n")
    user_input.clear()
    user_input.refresh()
    notrase(show_chat, msg, 0, 1)
    msg = "Writing to file, please wait..."
    show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    show_chat.refresh()
    time.sleep(1)
    notrase(show_chat, msg, 0, 1)
    msg = "Username updated!"
    show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    show_chat.refresh()
    time.sleep(1)
    notrase(show_chat, msg, 1, 1)

def set_qkeys(stdscr, show_chat, tbox, user_input):
    with open(""):
        return

def importip(stdscr, show_chat, tbox, user_input):
    global ipid, alias
    user_input.clear()
    user_input.refresh()
    msg1 = "This will assist you in connecting to networks"
    show_chat.addstr(y + 1, 0, msg1, HIGHLIGHT_1)
    msg2 = "We will assign an ID to an IP address"
    show_chat.addstr(y + 2, 0, msg2, HIGHLIGHT_1)
    msg3 = "please enter the IP address youd like to give an ID"
    show_chat.addstr(y + 3, 0, msg3, HIGHLIGHT_3)
    show_chat.refresh()
    inp = tbox.edit().strip()
    if inp:
        attr_dict["idaddr"] = inp.strip()
    user_input.clear()
    user_input.refresh()
    notrase(show_chat, msg1, 0, 1)
    notrase(show_chat, msg2, 0, 2)
    notrase(show_chat, msg3, 0, 3)
    msg1 = "For the ID, you can enter any number or text"
    show_chat.addstr(y + 1, 0, msg1, HIGHLIGHT_1)
    msg2 = "You can only have one ID total"
    show_chat.addstr(y + 2, 0, msg2, HIGHLIGHT_1)
    msg3 = "please enter the ID to be assigned"
    show_chat.addstr(y + 3, 0, msg3, HIGHLIGHT_3)
    show_chat.refresh()
    inp = tbox.edit().strip()
    if inp:
        attr_dict["alias"] = inp.strip()
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, val in attr_dict.items():
                file.write(f"{title}={val}\n")
    user_input.clear()
    user_input.refresh()
    notrase(show_chat, msg1, 0, 1)
    notrase(show_chat, msg2, 0, 2)
    notrase(show_chat, msg3, 0, 3)
    msg = "Writing to file, please wait..."
    show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    show_chat.refresh()
    time.sleep(1)
    notrase(show_chat, msg, 0, 1)
    msg = "Connection ID added. To skip the connection process entirely, configure #autostart"
    show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    show_chat.refresh()
    time.sleep(1)
    notrase(show_chat, msg, 1, 1)

commands = {"#help": listcmd, "#exit": shutoff, "#query-user": query, "#add-user": savenick, "#change-user": changeuser, "#autoconnect":auto_conf, "#import-ip":importip, "#clear": clr}

#$
def message(tbox, user_input, top_win, show_chat, stdscr):
    global y
    x = 0
    while True:
        try:
            inp = tbox.edit().strip()
            if inp:
                y += 2
                clearchk(show_chat)
                if "#" in inp and '"' not in inp:
                    xcute = commands.get(inp)
                    if xcute:
                        inp = xcute(stdscr, show_chat, tbox, user_input)
                    else:
                        inp = "invalid"
                    clearchk(stdscr)
                    if inp:
                        show_chat.addstr(y, x, inp, HIGHLIGHT_4)
                    user_input.erase()
                    user_input.refresh()
                    show_chat.refresh()
                    inp = None
                    continue
                
                if "server.main." not in inp or '"' in inp:
                    show_chat.addstr(y, x, inp, HIGHLIGHT_4)
                user_input.erase()
                user_input.refresh()
                show_chat.refresh()
                server.sendall(inp.encode("utf-8"))
                inp = None
        except KeyboardInterrupt:
                server.close()
                exit()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(height // 2, width // 2, str(e))
            stdscr.refresh()

def config_init(show_chat, user_input, tbox):
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
                manual_conf(show_chat, user_input, tbox, "false")
    except Exception as e:
        with open(f"{conf_path}/errlog.txt", "a") as file:
            file.write(f"ERROR ERROR ERROR\n\n{str(e)}\n\n")
            for name, val in attr_dict.items():
                file.write(f"attr: {name} = {val}")
            file.write(f"ERROR END\n")
        manual_conf(show_chat, user_input, tbox, "true")

def manual_conf(show_chat, user_input, tbox, state):
    global ip, username, network, server
    os.makedirs(conf_path, exist_ok=True)
    user_input.clear()
    user_input.refresh()
    if state == "true":
        msg1 = "It looks like its your first time starting the messenger."
        msg2 = "Lets start by getting the username youd like to use"
        show_chat.addstr(y + 1, 0, msg1, HIGHLIGHT_1)
        show_chat.addstr(y + 2, 0, msg2, HIGHLIGHT_1)
    else:
        pass
    msg3 = "please enter your desired username"
    show_chat.addstr(y + 3, 0, msg3, HIGHLIGHT_3)
    show_chat.refresh()
    inp = tbox.edit().strip()
    if inp:
        attr_dict["name"] = inp.strip()
    user_input.clear()
    user_input.refresh()
    if state == "true":
        notrase(show_chat, msg1, 0, 1)
        notrase(show_chat, msg2, 0, 2)
        msg1 = "Next enter the IP address of the message server your connecting to"
        show_chat.addstr(y + 1, 0, msg1, HIGHLIGHT_1)
        msg2 = "If you are hosting the server yourself, 'localhost' will work"
        show_chat.addstr(y + 2, 0, msg2, HIGHLIGHT_1)
    notrase(show_chat, msg3, 0, 3)
    msg3 = "please enter the IP to connect to"
    show_chat.addstr(y + 3, 0, msg3, HIGHLIGHT_3)
    show_chat.refresh()
    inp = tbox.edit().strip()
    if inp:
        attr_dict["ipaddr"] = inp.strip()
    user_input.clear()
    user_input.refresh()
    if state == "true":
        notrase(show_chat, msg1, 0, 1)
        notrase(show_chat, msg2, 0, 2)
        msg = "Writing to file, please wait..."
        show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    notrase(show_chat, msg3, 0, 3)
    show_chat.refresh()
    time.sleep(1)
    if state == "true":
        notrase(show_chat, msg, 0, 1)
    msg = "Attempting connect. To skip the connection process entirely, configure #autostart"
    show_chat.addstr(y + 1, 0, msg, HIGHLIGHT_1)
    show_chat.refresh()
    time.sleep(1)
    notrase(show_chat, msg, 1, 1)
    if state == "true":
        with open(f"{conf_path}/msg_server.conf", "w") as file:
            for title, data in attr_dict.items():
                file.write(f"{title}={data}\n")
    server = netcom.socket(ipv4, tcp)
    server.connect((ip, port))
    server.sendall(attr_dict["name"].encode("utf-8"))
    network = "connected!    "
    msg3 = "Connection accepted! Moving to shell.."
    show_chat.addstr(y // 2, width // 2 - len(msg3), msg3, HIGHLIGHT_3)
    show_chat.refresh()
    time.sleep(1)
    show_chat.clear()
    show_chat.refresh()

def autoconnect(show_chat, user_input, tbox):
    global ip, username, network, server
    with open(f"{conf_path}/msg_server.conf", "r") as file:
        attrs = file.readlines()
        for item in attrs:
            title, val = item.split("=")
            attr_dict[title.strip()] = val.strip()
    show_chat.clear()
    show_chat.refresh()
    msg1 = f"Connecting to: {attr_dict['idaddr']}"
    show_chat.addstr(y + 1, 0, msg1, HIGHLIGHT_1)
    msg2 = f"Username: {attr_dict['name']}"
    show_chat.addstr(y + 2, 0, msg2, HIGHLIGHT_1)
    msg3 = "Waiting for accept..."
    show_chat.addstr(y + 3, 0, msg3, HIGHLIGHT_3)
    show_chat.refresh()
    time.sleep(1)
    server = netcom.socket(ipv4, tcp)
    server.connect((attr_dict["ipaddr"], port))
    server.sendall(attr_dict["name"].encode("utf-8"))
    network = "connected!    "
    show_chat.clear()
    msg3 = "Connection accepted! Moving to shell.."
    show_chat.addstr(y // 2, width // 2 - len(msg3), msg3, HIGHLIGHT_3)
    show_chat.refresh()
    time.sleep(1)
    show_chat.clear()
    show_chat.refresh()
wrapper(main)
