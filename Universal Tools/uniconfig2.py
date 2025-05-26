import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
import subprocess
height = 0
width = 0
offset = 1
done = 0
pos = 0
colors = {}
screens = {}
apps = ["ztime", "weathertool", "homescreen", "ztext", "ztext_srvr", "zget", "zapp_srvr", "zcall", "zcall_srvr", "znet", "zclock", "zbrowse", "zstore", "zstore_srvr", "zconf"]
apps_found = []
apps_confs = []
local_path = ""

def main(stdscr):
    global height, width, colors, screens
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
    lookforapps()
    print_list(screens, colors, apps_found)
    inps(screens, colors)

def lookforapps():
    global apps_found
    for item in os.listdir("/etc"):
        if item in apps:
            apps_found.append(item)
def lookforconfs():
    global apps_confs, local_path
    for item in os.listdir(f"/etc/{apps_found[pos]}"):
        if ".conf" in item:
            apps_confs.append(item)
    local_path = f"/etc/{apps_found[pos]}"

def print_list(screens, colors, listy):
    y = offset
    screens["main"].clear()
    for item in listy:
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()
def inps(screens, colors):
    global current, pos, apps_confs
    current = apps_found
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            select(screens, colors, key)
        elif key == ord("e") and current != apps_confs:
            lookforconfs()
            current = apps_confs
            print_list(screens, colors, apps_confs)
        elif key == ord(" ") and current == apps_confs:
            subprocess.call(["sudo", "nano", f"{local_path}/{apps_confs[pos]}"])
            print_list(screens, colors, apps_confs)
        elif key == ord("q"):
            pos = 0
            apps_confs = []
            current = apps_found
            print_list(screens, colors, apps_found)
        elif key == ord('\x1b'):
            exit()
def select(screens, colors, key):
    global pos
    if key == ord("s"):
        pos += 1
        if pos >= len(current):
            pos = len(current) - 1
        back = 1
        if pos <= 0:
            back = 0
    elif key == ord("w"):
        pos -= 1
        back = -1
        if pos <= 0:
            pos = 0
            back = 0
    screens["main"].addstr(pos + offset - back, 0, current[pos - back])
    screens["main"].addstr(pos + offset, 0, current[pos], colors["highlight"])

wrapper(main)
