#!/bin/env python3
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import curses
from curses.textpad import Textbox
from curses import wrapper
import socket as netcom
import os

curusr = os.path.expanduser("~")

conf_path = curusr+"/.zinapp/keyget"
flags = {"-w": "*%_@", "-c": "$@^#"}

cmd_list = ["Get Key", "Check Users", "Configure Autostart", "Exit"]

if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "keyget" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(conf_path)

if "wireguard" not in os.listdir("/etc"):
    print("wireguard is not installed.")
    exit()
else:
    print("wireguard is installed")

server = netcom.socket(ipv4, tcp)
port = 10592


screens = {}
colors = {}

def ref(screen):
    screen.clear()
    screen.refresh()

def main(stdscr):
    global height, width, colors, screens
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curpage = curses.color_pair(2)
    stdscr.clear()
    stdscr.refresh()
    top_bar = curses.newwin(0, width, 0, 0)
    main_win = curses.newwin(height - 5, width, 2, 0)
    link_win = curses.newwin(height - 5, (width // 3) - 1, 2, (width // 3) * 2)
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    tbox = Textbox(user_input)
    screens.update({"top": top_bar})
    screens.update({"main": main_win})
    screens.update({"box": user_input})
    screens.update({"text": tbox})
    screens.update({"source": stdscr})
    colors.update({"highlight": highlight})
    print_text(main_win, "Enter IP Address:", 0)
    ip = tbox.edit().strip()
    if not ip:
        ip = "localhost"
    server.connect((ip, port))
    server.recv(3)
    server.send("ack".encode("utf-8"))
    ref(main_win)
    inps(screens, colors)



def inps(screens, colors):
    while True:
        pos = 0
        executed = 0
        ref(screens["main"])
        print_list(screens["main"], cmd_list, 0, 0)
        while True:
            key = screens["main"].getch()
            if key == ord("s") or key == ord("w"):
                pos = select(pos, key, screens["main"], cmd_list)
            elif key == ord('\x1b'):
                exit()
            elif key == ord("e"):
                choice = cmd_list[pos]
                if choice == "Configure Autostart":
                    auto_start()
                    print_list(screens["main"], cmd_list, 0, 0)
                    continue
                elif choice == "Get Key":
                    choice = "get"
                elif choice == "Check Users":
                    search()
                    print_list(screens["main"], cmd_list, 0, 0)
                    continue
                elif choice == "Exit":
                    exit()
                server.send((choice.lower()).encode("utf-8"))
                response = server.recv(4186).decode("utf-8")
                for key, val in flags.items():
                    if val in response:
                        response = response.strip(val)
                        xcute = cmd.get(key)
                        if xcute:
                            xcute(response)
                            executed = 1
                            break
                if not executed:
                    display(response)
                break

def simple_text():
    inp = screens["text"].edit().strip()
    ref(screens["box"])
    return inp

def display(text):
    print_text(screens["main"], text, 5)
    screens["main"].getch()
    ref(screens["main"])

def simple_input(screen, menu):
    pos = 0
    print_list(screen, menu, 0, 0)
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

def auto_start():
    print_text(screens["top"], "Select daemon type for autostart", 5) 
    menu = ["1. Systemd", "2. Runit"]
    inp = simple_input(screens["main"], menu)

    if "1" in inp:
        ref(screens["top"])
        ref(screens["main"])
        print_text(screens["main"], "Wireguard on Systemd installations usually already creates a service for itself.", 5)
        print_text(screens["main"], "This exists at /etc/systemd/system", 6)
        inp = simple_input(screens["main"], ["Yes", "No"])
        if "y" not in inp.lower():
            return
        ref(screens["main"])
        with open("/etc/systemd/system/wg-quick@.service", "w") as file:
            file.write("[Unit]\nDescription=WireGuard via wg-quick(8) for %I\nAfter=network.target\nDocumentation=man:wg-quick(8)\nDocumentation=man:wg(8)\nDocumentation=https://www.wireguard.com/\nDocumentation=https://www.wireguard.com/quickstart/\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/usr/bin/wg-quick up %i\nExecStop=/usr/bin/wg-quick down %i\nExecReload=/usr/bin/wg-quick down %i ; /usr/bin/wg-quick up %i\nEnvironment=WG_ENDPOINT_RESOLUTION_RETRIES=infinity\n[Install]\nWantedBy=multi-user.target")    
        print_text(screens["main"], "wg-quick@.service written. if needed, run 'systemctl daemon-reload' and 'systemctl enable wg-quick@wg0.service'", 5)
    elif "2" in inp:
        start_path = "/etc/runit/runsvdir/default/wg"
        os.makedirs(start_path, exist_ok=True)
        with open(start_path+"/run", "w") as file:
            file.write("#!/bin/sh\necho 'RUN: attempting wireguard start' > /dev/kmsg\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nexport PATH\nexec 2>&1\nWG_CONF='/etc/wireguard/wg0.conf'\nsleep 5\nif [ -f $WG_CONF ]; then\n    echo 'RUN: Starting wg0...' > /dev/kmsg\n    wg-quick up $WG_CONF\nelse\n    echo 'RUN: wireguard config not found' > /dev/kmsg\n    exit 1\nfi\necho 'RUN: wireguard brought up successfully' > /dev/kmsg\nexec tail -f /dev/null")
        with open(start_path+"/finish", "w") as file:
            file.write("#!/bin/sh\necho 'RUN: attempting to bring wireguard down' > /dev/kmsg\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nexport PATH\nexec 2>&1\nWG_CONF='/etc/wireguard/wg0.conf'\nif [ -f $WG_CONF ]; then\n    echo 'RUN: Bringing down wg0...' > /dev/kmsg\n    wg-quick down $WG_CONF\nelse\n    echo 'RUN: WireGuard config not found at $WG_CONF' > /dev/kmsg\nfi\nexit 1")
        os.chmod(start_path+"/run", 0o755)
        os.chmod(start_path+"/finish", 0o755)
        ref(screens["main"])
        print_text(screens["main"], "run and finish file created, if needed, run 'sudo sv enable wg' to enable at start", 5)
        screens["main"].getch()
    else:
        return
    ref(screens["main"])

def download(arg):
    ref(screens["main"])
    print_text(screens["main"], arg, 5)
    inp = simple_input(screens["main"], ["Yes", "No"])
    server.send((inp.lower()).encode("utf-8"))
    response = server.recv(4186).decode("utf-8")
    ref(screens["main"])
    print_text(screens["main"], response, 5)
    inp = simple_text()
    server.send(inp.encode("utf-8"))
    response = server.recv(4186).decode("utf-8")
    ref(screens["main"])
    print_text(screens["main"], response, 5)
    inp = simple_input(screens["main"], ["1. Normal File", "2. Isolated File"])
    server.send(inp.encode("utf-8"))
    response = server.recv(4186).decode("utf-8")
    ref(screens["main"])
    data = response.strip(flags["-w"])
    ref(screens["main"])
    keys, data = data.split(":", 1)
    inp = simple_input(screens["main"], ["1. Dont save configuration file", "2. Save configuration file to current directory", "3. Save configuration file to /etc/wireguard"])
    ref(screens["main"])
    if "1" in inp:
        print_text(screens["main"], data, 0)
        return
    elif "2" in inp:
        path = ""
    else:
        path = "/etc/wireguard/"
    with open(path+"wg0.conf", "w") as file:
        file.write(data)

    cache, keys = keys.split("=", 1)
    pubkey, privkey = keys.split("&")

    with open(path+"public.key", "w") as file:
        file.write(pubkey)
    cache, pubkey = pubkey.split("=", 1)
    with open(path+"private.key", "w") as file:
        file.write(privkey) 
    print_list(screens["main"], [f"file created at: {path}wg0.conf", f"pubkey created at {path}public.key", f"privkey created at {path}private.key"], 0, 0)
    screens["main"].getch()
    ref(screens["main"])

def search():
    ref(screens["main"])
    print_text(screens["main"], "Type out which user name you would like to check", 5)
    inp = simple_text()
    server.send(f"check {inp}".encode("utf-8"))
    response = server.recv(4196).decode("utf-8")
    response = response.strip(flags["-c"])
    ref(screens["main"])
    print_text(screens["main"], response, 5)
    screens["main"].getch()
    ref(screens["main"])

cmd = {"-w": download, "-c": search}

def select(pos, key, screen, page):
    if key == ord("s"):
        pos += 1
        if pos >= len(page):
            pos -= 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos < 0:
            pos = 0
        back = -1
    if len(page) > 1:
        screen.addstr(pos - back, 0, page[pos - back])
    screen.addstr(pos, 0, page[pos], colors["highlight"])
    return pos



def print_text(screen, string, y):
    to_print = []
    for char in string:
        if char == '\n':
            text, string = string.split('\n', 1)
            to_print.append(text)
    to_print.append(string)
    for item in to_print:
        if y >= height:
            break
        screen.addstr(y, 0, item)
        y += 1
    screen.refresh()


def print_list(screen, text_list, y, offset):
    cache_list = []
    for item in text_list:
        cache_list.append(item)
    if offset:
        screen.clear()
        while offset != 0:
            cache_list.remove(text_list[offset])
            offset -= 1
    for item in cache_list:
        if y >= height:
            break
        screen.addstr(y, 0, item)
        y += 1
    screen.refresh()


wrapper(main)

