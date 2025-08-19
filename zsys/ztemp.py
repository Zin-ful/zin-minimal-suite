import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox

height = 0
width = 0
colors = {}
screens = {}
modules = []

def main(stdscr):
    global height, width, colors, screens
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
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
    while True:
        if search_for_class("hwmon"):
            print_list(screens, colors, search_hwmon(), 1)
            save(str(search_hwmon()))
        elif search_for_class("thermal"):
            print_list(screens, colors, search_thermal(), 1)
        else:
            print_text(screens, colors, "no thermals found", 1)

def inps(screens, colors):
	while True:
		key = screens["main"].getch()
    

def select(key, screens, colors):
    global pos
    if key == ord("s"):
        pos += 1
        if pos >= len(modules):
            pos = len(modules) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    screens["main"].addstr(pos + offset - back, 0, modules[pos - back])
    screens["main"].addstr(pos + offset, 0, modules[pos], colors["highlight"])

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

def load_file(path):
    with open(path, "r") as file:
        value = file.read()
    return str(value)

def save(string):
    with open("faggot.txt", "w") as file:
        file.write(string)
def search_hwmon():
    tempratures = []
    path = "/sys/class/hwmon/"
    tree = os.listdir("/sys/class/hwmon")
    for i in range(64):
        folder_names = [f"hwmon{i}", f"thermal_zone{i}"]
        file_names = ["name", f"temp{i}_input", "type", "temp"]
        values = ["coretemp", "k10temp", "x86_pkg_temp"]
        save(f"{path}{file_names[1]}")
        if folder_names[0] in tree:
            if file_names[1] in path + folder_names[0]:
                if load_file(file_names[0]) in values:
                    save(f"{path}{file_names[1]}")
                    tempratures.append(load_file(f"{path}{file_names[1]}"))     
    return tempratures


def search_thermal():
    tempratures = []
    tree = os.listdir("/sys/class/thermal")
    for i in range(64):
        folder_names = [f"hwmon{i}", f"thermal_zone{i}"]
        file_names = ["name", f"temp{i}_input", "type", "temp"]
        values = ["coretemp", "k10temp", "x86_pkg_temp"]
        if folder_names[2] in tree:
            if load_file(file_names[2]) in values:
                tempratures.append(load_file(file_names[3])) 
    return tempratures


def search_for_class(string):
    classes = os.listdir("/sys/class")
    if string in classes:
        return 1
    else:
        return 0

wrapper(main)