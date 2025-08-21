import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
current_note = []
ylimit = 6
height = 0
width = 0
pos = 0
ready = 0 #i fucking hate this ENTIRE variable and every time its called.
          #looking at this a month later im scared to update this program. I dont even remember what this variable is for
globalpos = 0
xpos = 0
colors = {}
screens = {}
truepath = ""

def main(stdscr):
    global height, width, colors, screens
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)

    stdscr.clear()
    stdscr.refresh()
    top_bar = curses.newwin(0, width, 0, 0)
    main_win = curses.newwin(height - 5, width, 2, 0)
    user_input = curses.newwin(1, width - 1, height // 2 + 4, width // 3)
    tbox = Textbox(user_input)
    screens.update({"top": top_bar})
    screens.update({"main": main_win})
    screens.update({"box": user_input})
    screens.update({"text": tbox})
    screens.update({"source": stdscr})
    colors.update({"highlight": highlight})
    newnote(screens, colors)
    
def inps(screens, colors):  
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            select(key, screens, colors)
        elif key == ord("a") or key == ord("d"):
            selectchar(key, screens, colors)
        elif key == ord("\n"):
            edit(screens, colors)
        elif key == ord("\x1b"):
            save_file()
            exit()

def newnote(screens, colors):
    global path, filename
    while True:
        screens["main"].clear()
        screens["main"].refresh()
        msg = "Type a name of an existing file to open it"
        screens["main"].addstr(height // 2 - 1, width // 2 - (len(msg) // 2), msg, colors["highlight"])
        msg = "Or type a new name to open a new file"
        screens["main"].addstr(height // 2, width // 2 - (len(msg) // 2), msg, colors["highlight"])
        screens["main"].refresh()
        inp = screens["text"].edit().strip()
        path = []
        if "/" in inp:
            cache = inp
            for item in inp:
                if item == "/":
                    part, cache = cache.strip("/", 1)
                    path.append(f"{part}/")
            filename = cache
            cache = path.copy()
            path = ""
            for item in cache:
                path += item
                path = path.strip()
        else:
            path = None
            filename = inp
        for item in os.listdir(path):
            if filename == item:
                open_file(screens, colors, path, item)
                continue
        create_file(path, filename)
        open_file(screens, colors, path, filename)

def save_file():
    with open(truepath, "w") as file:
        for item in current_note:
            file.write(item)

def create_file(path, filename):
    with open(f"{path}{filename}", "w") as file:
        file.write("")

def open_file(screens, colors, path, filename):
    global current_note, truepath
    screens["main"].clear()
    screens["main"].refresh()
    if not path:
        truepath = filename
    else:
        truepath = f"{path}{filename}"
    with open(truepath, "r") as file:
        current_note = file.readlines()
        i = 0
        while i < len(current_note):
            if not current_note[i].strip() or not current_note[i] or current_note[i] == '\n' or current_note[i].strip() == '\n' or current_note[i].strip() == "" or current_note[i].strip() == None or current_note[i].strip() == '\r\n':
                current_note.remove(current_note[i])
                current_note.insert(i, " \n")
            i += 1
        with open("3.txt", "w") as file:
            for item in current_note:
                file.write(item)
        print_list(screens, colors, current_note, 0, 0)
        inps(screens, colors)
    
def edit(screens, colors):
    global current_note, pos, xpos
    tempbox = curses.newwin(1, width - 1 - xpos, pos+globalpos + 2, xpos)
    editbox = Textbox(tempbox)
    line = current_note[pos+globalpos]
    for item in line[xpos:]:
        if line[xpos:] == " " or line[xpos:] == " \n":
            pass
        else:
            editbox._insert_printable_char(item)
    inp = editbox.edit().strip()
    current_note.remove(current_note[pos+globalpos]) 
    current_note.insert(pos+globalpos, f"{line[:xpos]}{inp}\n")
    print_list(screens, colors, current_note, 0, globalpos)
    with open("1.txt", "w") as file:
        file.write(str(current_note))
    
def select(key, screens, colors):
    global pos, globalpos, xpos, ready
    if key == ord("s"):
        ready = 0
        pos += 1
        if pos + globalpos >= len(current_note):
            pos -= 1
        back = 1
        if pos == height - ylimit:
            globalpos += pos
            pos = 0
            back = 0
            xpos = 0
            print_list(screens, colors, current_note, 0, globalpos)
        charback = current_note[pos + globalpos - back]
        char = current_note[pos + globalpos]
        if xpos >= len(char) - 1:
            xpos = 0
            screens["main"].addstr(pos - back, xpos, charback)
            screens["main"].addstr(pos, xpos, char[xpos], colors["highlight"])
        screens["main"].addstr(pos - back, xpos, charback[xpos])
        screens["main"].addstr(pos, xpos, char[xpos], colors["highlight"])
    elif key == ord("w"):
        pos -= 1
        back = -1
        if pos <= 0:
            pos = 0
            ready += 1
        else:
            ready = 0
        if pos == 0 and globalpos and ready > 1:
            ready = 0
            globalpos -= height - ylimit
            pos = height - ylimit - 1
            back = 0
            xpos = 0
            screens["main"].clear()
            print_list(screens, colors, current_note, 0, globalpos)
        charback = current_note[pos + globalpos - back]
        char = current_note[pos + globalpos]
        if xpos >= len(char) - 1:
            xpos = 0
            screens["main"].addstr(pos - back, xpos, charback)
            screens["main"].addstr(pos, xpos, char[xpos], colors["highlight"])
        screens["main"].addstr(pos - back, xpos, charback[xpos])
        screens["main"].addstr(pos, xpos, char[xpos], colors["highlight"])

def selectchar(key, screens, colors):
    global xpos
    if len(current_note[pos + globalpos]) <= 2:
        return
    if key == ord("d"):
        xpos += 1
        if xpos >= len(current_note[pos + globalpos]) - 1:
            xpos -= 1
        back = 1
        char = current_note[pos + globalpos]
        screens["main"].addstr(pos, xpos - back, char[xpos - back])
        screens["main"].addstr(pos, xpos, char[xpos], colors["highlight"])
    elif key == ord("a"):
        xpos -= 1
        if xpos <= 0:
            xpos = 0
        back = -1
        char = current_note[pos + globalpos]
        screens["main"].addstr(pos, xpos - back, char[xpos - back])
        screens["main"].addstr(pos, xpos, char[xpos], colors["highlight"])


def print_text(screens, colors, string, y):
    to_print = []
    for char in string:
        if char == '\n':
            text, string = string.split('\n', 1)
            to_print.append(text)
    to_print.append(string)
    for item in to_print:
        if y >= height - ylimit:
            break
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()


def print_list(screens, colors, text_list, y, offset):
    cache_list = []
    i = 0
    for item in text_list:
        cache_list.append(text_list[i])
        i += 1
    with open("1.txt", "w") as file:
        file.write(str(cache_list))
    if offset:
        screens["main"].clear()
        while offset:
            cache_list.remove(text_list[offset - 1])
            offset -= 1
        with open("2.txt", "w") as file:
            file.write(str(cache_list))
    for item in cache_list:
        if y >= height - ylimit:
            break
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()


wrapper(main)
