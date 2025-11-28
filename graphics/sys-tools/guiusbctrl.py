#!/usr/bin/env python3
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
colors = {}
screens = {}
mounts = []
pos = 0
offset = 2
def main(stdscr):
    global height, width, colors, screens
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    green = curses.color_pair(2)
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
    screens["top"].addstr(0,0, "mount or unmount a drive", green)
    screens["top"].refresh()
    getblocks(screens, colors)
    inps(screens, colors)

def actions(screens, colors, drive):
    global mounts, pos
    pos = 0
    if "<-mounted" in drive:
        mounted = 1
        drive = drive.strip("<-mounted")
    else:
        mounted = 0
    mounts = [f"mount drive {drive}", f"unmount drive {drive}"]
    print_list(screens, colors, mounts, 2)
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            select(key, screens, colors)
        elif key == ord("q"):
            break
        elif key == ord("e"):
            if pos == 0:
                if mounted:
                    screens["main"].clear()
                    screens["main"].addstr(3, 0, f"{drive} already mounted", colors["highlight"])
                    screens["main"].refresh()
                    while True:
                        key = screens["main"].getch()
                        if key:
                            break
                    print_list(screens, colors, mounts, 2)
                    continue
                os.makedirs("/mnt/drive", exist_ok=True)
                result = str(subprocess.run(["mount", f"/dev/{drive}", "/mnt/drive"], capture_output=True, text=True))
                if "Completed" not in result:
                    print_text(screens, colors, result, 2)
                    while True:
                        key = screens["main"].getch()
                        if key:
                            break
                break
            if pos == 1:
                if not mounted:
                    screens["main"].clear()
                    screens["main"].addstr(3, 0, f"{drive} is not mounted", colors["highlight"])
                    screens["main"].refresh()
                    while True:
                        key = screens["main"].getch()
                        if key:
                            break
                    print_list(screens, colors, mounts, 2)
                    continue
                result = str(subprocess.run(["umount", f"/dev/{drive}"], capture_output=True, text=True))
                if "Completed" not in result:
                    print_text(screens, colors, result, 2)
                    while True:
                        key = screens["main"].getch()
                        if key:
                            break
                break
def inps(screens, colors):
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            select(key, screens, colors)
        elif key == ord("e"):
            actions(screens, colors, mounts[pos])
            getblocks(screens, colors)
        elif key == ord('\x1b'):
            exit()

def select(key, screens, colors):
    global pos
    if key == ord("s"):
        pos += 1
        if pos >= len(mounts):
            pos = len(mounts) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    screens["main"].addstr(pos + offset - back, 0, mounts[pos - back])
    screens["main"].addstr(pos + offset, 0, mounts[pos], colors["highlight"])

def getblocks(screens, colors):
    global mounts
    blocks = subprocess.run(["lsblk", "--list"], capture_output=True, text=True)
    blocks = str(blocks.stdout)

    blks = []
    blockscache = blocks
    for item in blockscache:
        if item == '\n':
            cache, blocks = blocks.split('\n', 1)
            blks.append(cache)
    mounts = []
    for item in blks.copy():
        if "sd" in item or "mmc" in item:
            cache, idk = item.split(" ", 1)
            if "/" in item:
                cache += "<-mounted"
            if "/boot" in item:
                system = cache.replace('<-mounted', "")
                if "mmc" in system:
                    system = system.replace("p", "")
                for i in range(0, 10):
                    if str(i) in system:
                        system = system.strip(str(i))
                screens["top"].addstr(0, width // 3, f"{system} is likley your operating system")
                screens["top"].refresh()
            mounts.append(cache)
    print_list(screens, colors, mounts, 2)

def print_text(screens, colors, string, y):
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
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()


def print_list(screens, colors, text_list, y):
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
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()


wrapper(main)
