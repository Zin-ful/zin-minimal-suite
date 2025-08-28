from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import curses
from curses import wrapper
from curses.textpad import Textbox

height = 0
width = 0
colors = {}
screens = {}
pos = 0
ylimit = 6
globalpos = 0

conf_path = "/etc/keyget"
flags = {"-w": "*%_@"}

server = netcom.socket(ipv4, tcp)

ip = "localhost"
port = 10592

cmds = ["help", "get", "mkconf", "check", "list"]

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
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    tbox = Textbox(user_input)
    screens.update({"top": top_bar})
    screens.update({"main": main_win})
    screens.update({"box": user_input})
    screens.update({"text": tbox})
    screens.update({"source": stdscr})
    colors.update({"highlight": highlight})
    colors.update({"search": curpage})
	print_list(screens, colors, cmds, 0, globalpos)
    inps(screens, colors)

def inps(screens, colors):
    while True:
        screens["main"].getch()
		if key == ord("s") or key == ord("w"):
			select(key, screens, colors)
		if key == ord("e"):
			execute(cmds[pos])

def select(key, screens, colors):
    global pos, globalpos
    if key == ord("s"):
        pos += 1
        if pos + globalpos >= len(cmds) - 1:
            pos -= 1
        back = 1
        if pos == height - ylimit:
            globalpos += pos
            pos = 0
            back = 0
            print_list(screens, colors, cmds, 0, globalpos)
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
        if pos < 1 and globalpos:
            globalpos -= height - ylimit
            pos = height - ylimit - 1
            back = 0
            screens["main"].clear()
            print_list(screens, colors, cmds, 0, globalpos)
    
    screens["main"].addstr(pos - back, 0, cmds[pos + globalpos - back])
    screens["main"].addstr(pos, 0, cmds[pos + globalpos], colors["highlight"])

def print_text(screens, colors, string, y):
    to_print = []
    for char in string:
        if char == '\n':
            text, string = string.split('\n', 1)
            to_print.append(text)
    to_print.append(string)
    for item in cache_list:
        if y >= height - ylimit:
            break
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()


def print_list(screens, colors, text_list, y, offset):
    cache_list = []
    for item in text_list:
        cache_list.append(item)
    if offset:
        screens["main"].clear()
        while offset != 0:
            cache_list.remove(text_list[offset])
            offset -= 1
        with open("list2.txt", "w") as file:
            for item in cache_list:
                file.write(f"{item}\n")
    if not offset:
        with open("list.txt","w") as file:
            for item in cache_list:
                file.write(f"{item}\n")
    for item in cache_list:
        if y >= height - ylimit:
            break
        with open("text.txt", "w") as file:
            file.write(f"{item}\n")
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()

def userwait(screens):
    key = screens["main"].getch()
    if key:
        return key

"""Actual program functions"""

def init():
	if "keyget" not in os.listdir("/etc"):
		os.makedirs(conf_path, exist_ok=True)

	if "wireguard" not in os.listdir("/etc"):
		print("wireguard is not installed.")
		exit()
	else:
		print("wireguard is installed")
	cmd = {"-w": download}
	server.connect((ip, int(port)))
	ack = server.recv(3).decode("utf-8")
	if ack == "ack":
		server.send("ack".encode("utf-8"))

def execute(inp):
	server.send(inp.encode("utf-8"))
	response = server.recv(1024).decode("utf-8")
	for key, val in flags.items():
		if val in response:
			response = response.strip(val)
			xcute = cmd.get(key)
			if xcute:
				xcute(response)
				executed = 1
				break
	if executed:
		return response
	else:
		return 0

def download(screens, data):
	keys, data = data.split(":", 1)
	print_text(screens, colors, "Would you like to create a conf file?", 0)
	if "y" in userwait(screens):
		pass
	else:
		return 0

	print_text(screens, colors, "Would you like to create a conf file?", 0)
	if "y" in userwait(screens):
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
		print_test(screens, colors, f"file created at: {path}wg0.conf\npubkey created at {path}public.key\nprivkey created at {path}private.key", 0)


cmd = init()
wrapper(main)