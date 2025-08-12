import os
import threading as task
import time

import sys

height = 0
width = 0
colors = {}
screens = {}

def main(stdscr):
    global height, width, colors, screens
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)
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
    
 def inps(screens, colors)   
	while True:
		key = screens["main"].getch()
    

def select(key, screens, colors):
    global pos
    if key == ord("s"):
        pos += 1
        if pos >= len(applist):
            pos = len(applist) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    screens["main"].addstr(pos + offset - back, 0, applist[pos - back])
    screens["main"].addstr(pos + offset, 0, applist[pos], colors["highlight"])

def print_text(screens, colors, string, y):
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



