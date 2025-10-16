import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox

active = 1
height = 0
width = 0
colors = {}
values = ["coretemp", "k10temp", "x86_pkg_temp", "zenpower", "nct6775"]
screens = {}
update_time = 0.500
cputype = None

detail = 1000

def main(stdscr):
    global height, width, colors, screens, color, warm, hot, cold, default
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    default = curses.color_pair(1)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    cold = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    warm = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    hot = curses.color_pair(3)
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
    inp_task = task.Thread(target=inps, args=[screens, colors])
    inp_task.start()
    while active:
        time.sleep(update_time)
        if search_for_class("hwmon"):
            temperatures = search_hwmon()
        if search_for_class("thermal"):
            temperatures_2 = search_thermal()
            for item in temperatures_2:
                temperatures.append(item)
        if not temperatures:
            print_text(1, screens, colors, "no thermals found", 1)
        else:
            color = get_color(temperatures)
            screens["main"].addstr(4, 0, "cpu type: " + cputype, color)
            msg = f"average temp all sensors: {avg(temperatures) // detail}"
            clear(screens, 5, 0, len(msg))
            screens["main"].addstr(5, 0, msg)
            print_list(0, screens, colors, temperatures, 7)
    inp_task.join()

def get_color(temperatures):
    average_temp = avg(temperatures)
    if average_temp < 40000:
        return cold
    elif average_temp > 40000 and average_temp < 75000:
        return warm
    elif average_temp > 75000:
        return hot
    else:
        return default

def inps(screens, colors):
    global update_time, active, detail
    update_val = 0.001
    while True:
        screens["main"].addstr(0, 0, "blue = cold, yellow = warm, red = hot. detail adds decimal points")
        msg = f"update interval: {update_time}; detail: {detail}"
        clear(screens, 1, 0, len(msg))
        screens["main"].addstr(1, 0, msg)
        screens["main"].addstr(2, 0, "(w/s and W/S or a/d to change values)")
        key = screens["main"].getch()
        if key == ord("w"):
            update_time = round(update_time + update_val, 8)
        elif key == ord("s"):
            update_time = round(update_time - update_val, 8)
        elif key == ord("W"):
            update_time = round(update_time + update_val * 10, 8)
        elif key == ord("S"):
            update_time = round(update_time - update_val * 10, 8)
        elif key == ord("a"):
            detail = detail / 10
            if detail < 1:
                detail = 1
        elif key == ord("d"):
            detail *= 10
            if detail > 10000:
                detail = 10000
        else:
            break
        
        if update_time < 0.001:
            update_time = 0.001
    active = 0        
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

def print_text(clr, screens, color, string, y):
    if clr:
        screens["main"].clear()
    to_print = []
    screens = {}
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

def clear(screens, y, x, item_len):
    item = ""
    for _ in range(item_len):
        item += "  "
    screens["main"].addstr(y, x, item)
    #screens["main"].refresh()

def avg(listy):
    total = 0
    for item in listy:
        total += int(item)
    return total // len(listy)

def print_list(clr, screens, colors, text_list, y):
    if clr:
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
        color = get_color(text_list)
        msg = "temp = " + str(int(item) // detail)
        clear(screens,y,0,len(msg))
        screens["main"].addstr(y, 0, msg, color)
        y += 1
    screens["main"].refresh()

def load_file(spl, path):
    if spl:
        file_path, name = path.split(":")
        try:
            with open(file_path+name, "r") as file:
                value = file.read()
            return str(value)
        except:
            pass
    else:
        with open(path, "r") as file:
            value = file.read()
        return str(value)

def search_hwmon():
    global cputype
    tempratures = []
    path = "/sys/class/hwmon/"
    tree = os.listdir("/sys/class/hwmon")
    for i in range(64):
        if f"hwmon{i}" in tree:
            if "name" in os.listdir(path + f"hwmon{i}"):
                name = load_file(0, path +f"hwmon{i}/name")
                if not cputype:
                    if name in "k10temp":
                        cputype = "AMD cpu"
                    elif name in "coretemp":
                        cputype = "INTEL cpu"
                    else:
                        cputype = "cpu"
                if name.strip() in values:
                    for j in range(64):
                        temp_value = load_file(1, f"{path}:{f'hwmon{i}/temp{j}_input'}")
                        if temp_value:
                            tempratures.append(temp_value)     
    return tempratures

def search_thermal():
    tempratures = []
    path = "/sys/class/thermal/"
    tree = os.listdir("/sys/class/thermal")
    for i in range(64):
        if f"thermal_zone{i}" in tree:
            if "type" in os.listdir(path + f"thermal_zone{i}"):
                name = load_file(0, path +f"thermal_zone{i}/type")
                if name.strip() in values:
                    for j in range(64):
                        temp_value = load_file(1, f"{path}:{f'thermal_zone{i}/temp'}")
                        if temp_value:
                            tempratures.append(temp_value)     
    return tempratures


def search_for_class(string):
    classes = os.listdir("/sys/class")
    if string in classes:
        return 1
    else:
        return 0

wrapper(main)