import curses
from curses import wrapper
from curses.textpad import Textbox
import os
import threading

pos = 0
yplus = 0
cur_dir = os.path.dirname(os.path.abspath(__file__))
files_in_path = os.listdir(cur_dir)
SELECT = None


def main(stdscr):
    global SELECT, height, width
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    SELECT = curses.color_pair(1)
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.refresh()
    files_win = curses.newwin(height - 4, width - 1, 2, 0)
    menu_win = curses.newwin(height // 2, width // 6, 0, width // 6)
    files_win.timeout(10)
    win = {"main": stdscr, "files": files_win, "menu": menu_win}
    list_file(win)
    inps(win)

def list_file(win):
    global files_in_path, pos
    #pos = 0
    win["files"].clear()
    files_in_path = os.listdir(cur_dir)
    i = 0
    y = 0
    x = 0
    for item in files_in_path:
        if x >= width - 1:
            pass
        else:
            win["files"].addstr(y, x, item, curses.COLOR_WHITE)
        i += 1
        y += 1
        if y >= height - height // 10:
            x += width // 3 - 1
            y = 0
    win["files"].refresh()

def inps(win):
    global cur_dir
    while True:
        key = win["files"].getch()
        if key == -1:
            continue
        if key == ord("q") or key == ord("e"):
            cur_dir = move(key)
            list_file(win)
            win["files"].refresh()
        elif key == ord("w") or key == ord("s"):
            select(win, key)

def menu():
    return


def select(win, inp):
    global pos, yplus
    if not files_in_path or len(files_in_path) < 0:
        win["files"].addstr(height // 3, width // 2, "NO FILES IN PATH", SELECT)
        win["files"].refresh()
        return
    x = 0
    y = 0
    lvl = 0
    if inp == ord("s"):
        pos += 1
        offset = 1
    elif inp == ord("w"):
        offset = -1
        pos -= 1
    else:
        return
    prevlen = ""
    if pos >= height - 5 and len(files_in_path) > height - 5:
        pos = 0
        lvl += 1
        x += width // 3 - 1
    elif pos < 0 and lvl >= 1:
        x -= width // 3 - 1
        pos = height - 4
        lvl -= 1
    if pos <= 0:
        offset = 0
        pos = 0
    elif pos >= len(files_in_path):
        pos = len(files_in_path) - 1
        offset = 0
    for i in files_in_path[pos]:
        prevlen += " "
    if pos > -1:
        win["files"].addstr(y + pos - offset, x, prevlen, curses.COLOR_BLACK)
        win["files"].addstr(y + pos - offset, x, files_in_path[pos - offset], curses.COLOR_BLACK)
    win["files"].addstr(y + pos, x, files_in_path[pos], SELECT)
    win["files"].refresh()

def open_file():
    return

def copy_file():
    return

def del_file():
    return

def refresh():
    return

def paste_file():
    return

def move(inp):
    rev_dir = os.path.dirname(f"{cur_dir}..")
    if files_in_path or len(files_in_path) > 0:
        forw_dir = cur_dir + "/" + files_in_path[pos]
    if inp == ord("q"):
        if cur_dir == "/":
            return "/"
        else:
            try:
                var = os.listdir(rev_dir)
            except:
                return cur_dir
            return rev_dir
    elif inp == ord("e"):
        try:
            var = os.listdir(forw_dir)
        except:
            return rev_dir
        return forw_dir

wrapper(main)
