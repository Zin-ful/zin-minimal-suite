from socket import SOCK_STREAM as tcp
from socket import AF_INET as ipv4
import socket as netcom
import os
import threading as task
import curses
from curses import wrapper
from curses.textpad import Textbox

port = 34983

pos = 0
sx = 0
lvl = 0
origin = 0
num = 0
screens = {}
colors = {}
header_size = 10

ylimit = 1

tv = {}
movies = {}
anime = {}

curusr = os.path.expanduser("~")

conf_path = curusr+ "/.zinapp/zranking/"

if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "zranking" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(curusr+"/.zinapp/zranking")


def generate_theme(selection):
    #black, red green, yellow, blue, magenta, cyan, white
    curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)
    if selection == "berries_one":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    elif selection == "berries_two":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
    elif selection == "berries_three":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    elif selection == "hearts":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    elif selection == "leaves":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_GREEN)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_YELLOW)
    elif selection == "standard":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
    elif selection == "cool":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_WHITE)
    elif selection == "sunny":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    elif selection == "cloudy":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    elif selection == "lava":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_WHITE)
    elif selection == "water":
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)


    HIGHLIGHT_1 = curses.color_pair(1)
    HIGHLIGHT_2 = curses.color_pair(2)
    HIGHLIGHT_3 = curses.color_pair(3)
    HIGHLIGHT_4 = curses.color_pair(4)
    HIGHLIGHT_5 = curses.color_pair(5)
    FROM_SERVER = curses.color_pair(6)
    BATHIGH = curses.color_pair(7)
    BATNORM = curses.color_pair(8)
    BATLOW = curses.color_pair(9)

    colors.update({"high":BATHIGH})
    colors.update({"norm":BATNORM})
    colors.update({"low":BATLOW})
    colors.update({"hl":HIGHLIGHT_1})
    colors.update({"hl1":HIGHLIGHT_2})
    colors.update({"hl2":HIGHLIGHT_3})
    colors.update({"hl3":HIGHLIGHT_4})
    colors.update({"hl4":HIGHLIGHT_5})
    colors.update({"server":FROM_SERVER})


def main(stdscr):
    global height, width
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.refresh()

    user_input = curses.newwin(1, width - 1, height - 2, 1)
    tbox = Textbox(user_input)

    screens.update({"input":user_input})
    screens.update({"text":tbox})
    screens.update({"source":stdscr})
    generate_theme("standard")
    menu = ["Online", "Offline"]
    while True:
        choice = dynamic_inps(menu, 2)
        if "On" in choice:
            pass
        else:
            offline_menu()

def offline_menu():
    ref(screens["source"])
    menu = ["Rate Items", "View Ratings"]
    choice = dynamic_inps(menu, 2)
    if "Rate" in choice:
        rate_menu()
    else:
        view_menu()
def rate_menu():
    ref(screens["source"])
    print_text(0, 0, (f"Rating Menu",))
    menu = ["Anime", "TV", "Movies"]
    choice = dynamic_inps(menu, 2)
    if "A" in choice:
        criteria = ["Animation Quality", "Music", "Story", "Direction", "Creativity", "Pacing"]
    else:
        criteria = ["Acting", "FX", "Direction", "Story", "Consistency"]
    rate(choice, criteria)

def view_menu():
    ref(screens["source"])
    print_text(0, 0, (f"Viewing Menu",))
    menu = ["Anime", "TV Show", "Movie"]
    choice = dynamic_inps(menu, 2)
    if "A" in choice:
        listy = []
        for name, val in anime.items():
            listy.append(f"{name}:{val}")
    ref(screens["source"])
    if listy:
        print_list(0, 0, listy)
    else:
        print_text(0, 0, ("Nothing to see!",))
    screens["source"].getch()
    ref(screens["source"])


def rate(type, criteria):
    while True:
        ref(screens["source"])
        print_text(0, 0, (f"Enter the name of the {type} your going to rate.",))
        name = get_input()
        print_text(0, 0, (f"                                                ",))
        ratings = {}
        for item in criteria:
            print_text(0, 0, (f"Out of 10, please rate the {item} of {name}",))
            rating = get_input()
            ref(screens["source"])
            try:
                rating = int(rating)
                if rating > 10:
                    break
                ratings.update({item:rating})
            except:
                break
        check = []
        if not ratings:
            continue
        for item, val in ratings.items():
            check.append(item)
        if len(check) != len(criteria):
            continue
        
        total_score = sum(ratings.values())
        max_score = len(criteria) * 10
        percentage = (total_score / max_score) * 100
        ref(screens["source"])
        if "A" in type:
            anime.update({name:percentage})
        elif "T" in type:
            tv.update({name:percentage})
        else:
            movies.update({name:percentage})

        save(type)
        print_text(0, 0, ("Final score:", f"{name} = {percentage}%"))
        screens["source"].getch()

def save(type):
    if "A" in type:
        with open(conf_path + "anime.txt", "w") as file:
            for name, val in anime.items():
                file.write(f"{name}={val}\n")
    elif "T" in type:
        with open(conf_path + "tv.txt", "w") as file:
            for name, val in tv.items():
                file.write(f"{name}={val}\n")
    else:
        with open(conf_path + "movies.txt", "w") as file:
            for name, val in movies.items():
                file.write(f"{name}={val}\n")

def load():
    if "anime.txt" in os.listdir(conf_path):
        with open(conf_path + "anime.txt", "r") as file:
            lines = file.readlines()
            for item in lines:
                name, value = item.split("=")
                anime.update({name.strip(): float(value.strip())})
    elif "tv.txt" in os.listdir(conf_path):
        with open(conf_path + "tv.txt", "r") as file:
            lines = file.readlines()
            for item in lines:
                name, value = item.split("=")
                tv.update({name.strip(): float(value.strip())})
    elif "movies.txt" in os.listdir(conf_path):
        with open(conf_path + "movies.txt", "r") as file:
            lines = file.readlines()
            for item in lines:
                name, value = item.split("=")
                movies.update({name.strip(): float(value.strip())})

def get_input():
    inp = screens["text"].edit().strip()
    ref(screens["input"])
    if inp:
        return inp

def inps(menu):
    print_list(0, 0, menu)
    pos = 0
    while True:
        inp = screens["source"].getch()
        if inp == ord("e"):
            return menu[pos]
        elif inp == ord("w") or inp == ord("s"):
            pos = select(menu, inp, pos)
        elif inp == ord("R"):
            screens["source"].clear()
            screens["source"].refresh()
            print_list(0, 0, menu)

def dynamic_inps(menu, offset):
    print_list(0 + offset, 0, menu)
    pos = 0
    while True:
        inp = screens["source"].getch()
        if inp == ord("e"):
            return menu[pos]
        elif inp == ord("w") or inp == ord("s"):
            pos = dynamic_select(menu, inp, pos, offset)
        elif inp == ord("R"):
            screens["source"].clear()
            screens["source"].refresh()
            print_list(0 + offset, 0, menu)
        elif inp == ord("q"):
            return 0

def dynamic_select(menu, key, pos, offset):
    if key == ord("s"):
        pos += 1
        if pos >= len(menu):
            pos = len(menu) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    if len(menu) > 1:
        screens["source"].addstr(pos - back + offset, 0, menu[pos - back])
    screens["source"].addstr(pos + offset, 0, menu[pos], colors["hl1"])
    return pos

def print_list(y, x, menu):
    i = 0
    for item in menu:
        screens["source"].addstr(y + i, x, item)
        i += 1
    screens["source"].refresh()
    return i

def print_text(pos_y, pos_x, msg, color=None):
    i = 0
    for item in msg:
        screens["source"].addstr(pos_y + i, pos_x, item)
        i += 1
    screens["source"].refresh()


def ref(screen):
    screen.clear()
    screen.refresh()

def print_list_scr(y, x, menu, scr):
    i = 0
    for item in menu:
        scr.addstr(y + i, x, item)
        i += 1
    scr.refresh()
    return i

load()
wrapper(main)