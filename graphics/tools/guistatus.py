#!/usr/bin/env python3
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import time
import threading as task
import curses
from curses import wrapper
from curses.textpad import Textbox

port = 23512

server = netcom.socket(ipv4, tcp)
ip = input("IP? >>> ")
server.connect((ip, int(port)))

height = 0
width = 0
colors = {}
screens = {}
pos = 0
ylimit = 6
globalpos = 0


def main(stdscr):
    global height, width
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
    check_thread = task.Thread(target=client_start, args=[screens, colors])
    check_thread.start()
    inps(screens, colors)

def inps(screens, colors):
    while True:
        screens["main"].getch()
        if key == ord('\x1b'):
            exit()

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

def client_start(screens, colors):
    while True:
        server.send("ack".encode("utf-8"))
        status = server.recv(1024).decode("utf-8")
        print_list(screens, colors, nltolist(status), 0, 0)
        time.sleep(1)

def nltolist(string):
    new_list = []
    cpy = string
    for i in cpy:
        if i == '\n':
            line, string = string.split('\n', 1)
            new_list.append(line)
    return new_list



wrapper(main)
