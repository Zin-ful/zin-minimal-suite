import curses
from curses import wrapper
from curses.textpad import Textbox
import os
import threading
import time
import subprocess
import signal

data_name = ""
data_path = ""

pos = 0
sx = 0
lvl = 0
origin = 0
num = 0

ylimit = 5

cur_dir = os.path.dirname(os.path.abspath(__file__))
files_in_path = os.listdir(cur_dir)
SELECT = None
data = None
hidden = 1
chunk_size = 4192
conf_path = "/etc/zbrowse"

if "zbrowse" not in os.listdir("/etc"):
    os.makedirs(conf_path, exist_ok=True)
if "trash" not in os.listdir(conf_path):
    os.makedirs(f"{conf_path}/trash", exist_ok=True)

def main(stdscr):
    global SELECT, height, width
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    SELECT = curses.color_pair(1)
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.refresh()
    files_win = curses.newwin(height - 4, width - 1, 2, 0)
    menu_win = curses.newwin(height - 1, width - 10, 0, 10)
    files_win.timeout(10)
    win = {"main": stdscr, "files": files_win, "menu": menu_win}
    list_file(win, 0.02, 1)
    inps(win)

def list_file(win, delay, rst):
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
        if y >= height - height // 10:
            x += width // 3 #if statement makes zero sense
            y = 0
        time.sleep(delay)
        win["files"].refresh()

def log(string):
    with open("log.txt", "w") as file:
        file.write(f"START: {string} {pos} {lvl}\n")
        for i in files_in_path:
            file.write(f"{i}\n")
        file.write("END\n")

def inps(win):
    global cur_dir, pos, origin
    while True:
        key = win["files"].getch()
        if key == -1:
            continue
        if key == ord("a") or key == ord("d"):
            cur_dir = move(key)
            list_file(win, 0.002, 1)
            win["files"].refresh()
        elif key == ord("w") or key == ord("s"):
            select(win, key, "files", files_in_path, None)
        elif key == ord("e"):
            origin = pos
            menu(win)
            origin = 0
        elif key == ord('\x1b'):
            exit()

def menu(win):
    global pos, menu_win
    cache = 0
    if pos >= height - 10:
        offset = 0
    else:
        offset = 0
    if len(files_in_path) > 0:
        for i in files_in_path:
            if not cache:
                cache = len(i)
            if len(i) > cache:
                cache = len(i)

    pos = 0
    win["menu"].addstr(origin - offset, sx + cache, "Copy ", curses.COLOR_WHITE)
    win["menu"].addstr(origin + 1 - offset, sx + cache, "Paste ", curses.COLOR_WHITE)
    win["menu"].addstr(origin + 2 - offset, sx + cache, "Delete ", curses.COLOR_WHITE)
    win["menu"].addstr(origin + 3 - offset, sx + cache, "Edit ", curses.COLOR_WHITE)
    options = ["Copy ", "Paste ", "Delete ", "Edit "]
    x = 0
    while True:
        if x:
            win["menu"].addstr(origin - offset, sx + cache, "     ", curses.COLOR_WHITE)
            win["menu"].addstr(origin + 1 - offset, sx + cache, "      ", curses.COLOR_WHITE)
            win["menu"].addstr(origin + 2 - offset, sx + cache, "       ", curses.COLOR_WHITE)
            win["menu"].addstr(origin + 3 - offset, sx + cache, "     ", curses.COLOR_WHITE)
            win["menu"].refresh()
            pos = origin
            return
        inp = win["menu"].getch()
        if inp == -1:
            continue
        if inp == ord("w") or inp == ord("s"):
            select(win, inp, "menu", options, cache)
        elif inp == ord("q"):
            x = 1
        elif inp == ord("e"):
            xcute = actions.get(options[pos])
            if xcute:
                xcute(win)
                x = 1

def select(win, inp, subwin, word_list, xoffset):
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
        pos = height - 5
        lvl -= 1
        if sx < 0 and num:
            num -= 3
            list_file(win, 0.002, 0)
            sx = (width - width // 3) - 2

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
        win[subwin].addstr(origin + pos, sx + xoffset, word_list[pos + lvl_offset], SELECT)
    else:
        if pos > -1:
            win[subwin].addstr(final_pos, sx + xoffset, prevlen, curses.COLOR_BLACK)
            win[subwin].addstr(final_pos, sx + xoffset, word_list[pos - offset], curses.COLOR_BLACK)
        win[subwin].addstr(origin + pos, sx + xoffset, word_list[pos], SELECT)
    win[subwin].refresh()

def edit(win):
    global origin
    origin = 0
    origint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        subprocess.call(["sudo", "nano", f"{cur_dir}/{files_in_path[origin]}"])
    finally:
        signal.signal(signal.SIGINT, origint)
        time.sleep(0.2)
        win["main"].clear()
        win["main"].refresh()
        list_file(win, 0.02, 1)
        inps(win)
def copy(win):
    global data_name, data_path
    data_name = files_in_path[origin]
    data_path = f"{cur_dir}/{files_in_path[origin]}"
    with open("errlog.txt", "w") as file:
        file.write(f"{data_name}\n{data_path}\n")
def paste(win):
    count = 1
    file_name = data_name
    for item in files_in_path:
        if item == file_name:
            file_name = f"{data_name.replace('_cpy{count-1}', '')}_cpy{count}"
            count += 1
    with open(data_path, "rb") as filer:
        filer.seek(0, 2)
        file_size = filer.tell()
        filer.seek(0)
        with open(f"{cur_dir}/{file_name}", "wb") as filew:
            while True:
                chunk = filer.read(chunk_size)
                if not chunk:
                    break
                filew.write(chunk)
    list_file(win, 0.002, 1)

def cache_file():
    count = 1
    file_name = data_name
    for item in files_in_path:
        if item == file_name:
            file_name = f"{data_name.replace('_cpy{count-1}', '')}_cpy{count}"
            count += 1
    with open(data_path, "rb") as filer:
        filer.seek(0, 2)
        file_size = filer.tell()
        filer.seek(0)
        with open(f"{conf_path}/trash/{file_name}", "wb") as filew:
            while True:
                chunk = filer.read(chunk_size)
                if not chunk:
                    break
                filew.write(chunk)
def delete(win):
    copy(win)
    cache_file()
    os.remove(f"{cur_dir}/{files_in_path[origin]}")
    list_file(win, 0.002, 1)
actions = {"Copy ": copy, "Paste ": paste, "Delete ": delete, "Edit ": edit}

def move(inp):
    rev_dir = os.path.dirname(f"{cur_dir}..")
    if files_in_path or len(files_in_path) > 0:
        if cur_dir == "/":
            forw_dir = cur_dir + files_in_path[num * sx + pos]
        else:
            if not num and sx:
                calc = (lvl * (height - ylimit)) + pos
                forw_dir = cur_dir + "/" + files_in_path[calc]
                log(f"CHECK ME {cur_dir + '/' + files_in_path[calc]}")
            else:
                calc = (lvl * (height - ylimit)) + pos
                forw_dir = cur_dir + "/" + files_in_path[calc]
                log(f"CHECK ME {cur_dir + '/' + files_in_path[calc]} {calc}")
    if inp == ord("a"):
        if cur_dir == "/":
            log(f"root: {cur_dir}")
            return "/"
        else:
            try:
                var = os.listdir(rev_dir)
            except:
                log(f"back: {cur_dir}")
                return cur_dir
            log(rev_dir)
            return rev_dir
    elif inp == ord("d"):
        try:
            var = os.listdir(forw_dir)
            log(f"forward: {forw_dir}")
        except:
            return cur_dir
        log(f"forward: {forw_dir}")
        return forw_dir

wrapper(main)
