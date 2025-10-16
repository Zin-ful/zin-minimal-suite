import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
import requests
import re
height = 0
width = 0
colors = {}
screens = {}
pos = 0
ylimit = 6
globalpos = 0
recentpage = ""
link = ""
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
    inps(screens, colors)

def inps(screens, colors):
    homepage(screens, colors)
    while True:
        pass

def homepage(screens, colors):
    global page, recentpage, link, pos, globalpos
    while True:
        screens["top"].clear()
        screens["main"].clear()
        homemsg = "Use links to visit webpages, ctrl + s to save your current link"
        screens["top"].addstr(0, 0, "HomePage", colors["search"])
        screens["main"].addstr(height // 3, width // 2 - (len(homemsg) // 2), homemsg, colors["highlight"])
        if recentpage:
            homemsg = f"last site: {recentpage}"
            screens["main"].addstr(height // 2, width // 2 - (len(homemsg) // 2), homemsg, colors["highlight"])
        screens["top"].refresh()
        screens["main"].refresh()

        page = []
        if not link:
            inp = screens["text"].edit().strip()
        else:
            inp = link
            link = ""
        screens["box"].clear()
        screens["box"].refresh()
        if "http" not in inp:
            inp = inp.strip("://")
            inp = f"https://{inp}"
        screens["top"].clear()
        if not len(inp) > width:
            screens["top"].addstr(0, 0, inp, colors["search"])
        screens["top"].refresh()
        try:
            pagedata = requests.get(inp)
            recentpage = inp
        except ConnectionError:
            homemsg = "Could not connect, check connection or URL?"
            screens["main"].addstr(height // 3, width // 2 - (len(homemsg) // 2), homemsg, colors["search"])
            continue
        except Exception as e:
            if "[Errno -3]" in str(e):
                homemsg = "Failure in name resolution, basically make sure the URL is valid OR you dont have internet"
            elif "[Errno -2]" in str(e):
                homemsg = f"URL is not known (URL no exist)"
            else:
                homemsg = f"Unknown Error: {str(e)}"
                if len(str(e)) > width:
                    homemsg1 = ""
                    """"i = 0
                    while i != len(str(e)) // 2:
                        homemsg1 += homemsg[i]
                        i += 1
                    homemsg.replace(homemsg1, "")
                    screens["main"].addstr(height // 3 - 1, width // 2 - (len(homemsg1) // 2), homemsg1, colors["highlight"])
                    screens["main"].addstr(height // 3, width // 2 - (len(homemsg) // 2), homemsg, colors["highlight"])"""
                    homemsg = "cant display error cause screen size"
            screens["main"].addstr(height // 3, width // 2 - (len(homemsg) // 2), homemsg, colors["highlight"])
            homemsg = "Press any key to continue"
            screens["main"].addstr(height // 2, width // 2 - (len(homemsg) // 2), homemsg, colors["highlight"])
            screens["main"].getch()
            continue
        fmtdata = str(pagedata.text)
        for item in fmtdata:
            if item == '\n':
                line, fmtdata = fmtdata.split('\n', 1)
                line = line.strip()
                if not line or line == " " or line == "\n":
                    continue
                elif len(line) > 1:
                    if line[len(line) - 1] == ";":
                        continue
                line = re.sub(r'{.*?}', '', line)
                if "href" in line:
                    stuff, line = line.split("=", 1)
                if re.sub(r'<.*?>', '', line):
                    line = re.sub(r'<.*?>', '', line)
                    if len(line) >= width:
                        while len(line) >= width:
                            line1 = line[len(line)//2:]
                            line = line[:len(line)//2]
                            page.append(line1)
                            page.append(line)
                    else:
                        page.append(line)
        for item in page:
            if item == "":
                page.remove(item)
        print_list(screens, colors, page, 0, 0)
        if not page:
            screens["main"].addstr(0,0, "this is your browser talking" )
            screens["main"].addstr(1,0, f"for some reason the requested webpage: {inp}" )
            screens["main"].addstr(2,0, f"had no data. press any key to go home" )

            key = screens["main"].getch()
            continue
        elif "404" in page[0]:
            key = screens["main"].getch()
            continue
        while True:    
            key = screens["main"].getch()
            if key == ord("s") or key == ord("w"):
                select(key, screens, colors)
            elif key == ord('\x1b'):
                break
            elif key == ord("e"):
                link = page[pos + globalpos].strip()
                pos = 0
                globalpos = 0
                break

def select(key, screens, colors):
    global pos, globalpos
    if key == ord("s"):
        pos += 1
        if pos + globalpos >= len(page) - 1:
            pos -= 1
        back = 1
        if pos == height - ylimit:
            globalpos += pos
            pos = 0
            back = 0
            print_list(screens, colors, page, 0, globalpos)
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
            print_list(screens, colors, page, 0, globalpos)
    
    screens["main"].addstr(pos - back, 0, page[pos + globalpos - back])
    screens["main"].addstr(pos, 0, page[pos + globalpos], colors["highlight"])

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


wrapper(main)

