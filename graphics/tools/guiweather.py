#!/usr/bin/env python3

import requests
import json
import threading
import os
from datetime import datetime
import sys
import time
import curses
from curses import wrapper
from curses.textpad import Textbox

curusr = os.path.expanduser("~")

conf_path = "/.zinapp/weathertool"
if ".zinapp" not in os.listdir(curusr):
	os.mkdir(curusr+"/.zinapp")
if "weathertool" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(curusr + conf_path)

conf_path = curusr + conf_path

print("Tool Version: 1.4\n")

name = ""
state = "TX"
county = "????"
bind_1 = "????"
bind_2 = "????"
bind_3 = "????"
center = "????"
NT = "????"
WT = "????"
ST = "????"
ET = "????"
NW = "????"
NE = "????" 
SW = "????" 
SE = "????"

url = "https://api.weather.gov/alerts/active?area="
times = {}
screens = {}
colors = {}

weather_types = {"surf": "water", "water": "water", "rain": "water", "flood": "water", "fog": "water", "hydro": "water", "wind": "wind", "heat": "heat", "dry":"heat", "fire": "heat", "red flag": "heat", "snow": "cold", "winter": "cold", "freeze": "cold", "frost": "cold", "spark": "spark", "light": "spark", "thunder": "spark", "storm": "spark"}
intense = ["extreme", "severe", "blizzard", "tornado", "hurri", "typhoon", "flood", "surge"]

parameters = {"state": state, "county": county, 
"center": center, "west": WT, "east": ET, "south": ST, "north": NT, 
"north east": NE, "south east": SE, "south west": SW, "north west": NW,  
"bind 1": bind_1, "bind 2": bind_2, "bind 3": bind_3}


directions = {"north":"N", "south":"S","west":"W", "east":"E", 
"south west":"SW", "south east":"SE","north west":"NW", "north east":"NE"}
            

sorting_phrases = ["warning", "alert", "outlook", "advisory", "watch"]


fetch_cmd = ["curl", "-s", url]
pos = 0
offset = 1
list_pos = 0

if "parameters.conf" not in os.listdir(conf_path):
    with open(f"{conf_path}/parameters.conf", "w") as file:
        for key, value in parameters.items():
            file.write(f"{key}={value}\n")
else:
    with open(f"{conf_path}/parameters.conf","r") as file:
        paradata = file.readlines()
        for item in paradata:
            if item == "" or item == " " or item == "\n":
                continue
            key, value = item.split("=")
            parameters[key] = value.strip().strip('\n')

fetch_time = 0
done = 0

def main(stdscr):
    global height, width
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)
    wet = curses.color_pair(2)
    cold = curses.color_pair(7)
    spark = curses.color_pair(3)
    heat = curses.color_pair(4)
    bad = curses.color_pair(5)
    wind = curses.color_pair(6)
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
    colors.update({"highlight": highlight, "water": wet, "spark": spark, "heat": heat, "bad": bad, "cold": cold, "wind": wind})
    inps()

def sort_list(text_list, top, middle, bottom, sortby):
    new_list = []
    t = 0
    if top or middle or bottom:
        for item in text_list:
            if top and top in item.lower():
                new_list.insert(0, item)
                t += 1
            elif middle and middle in item.lower():
                new_list.insert(t, item)
            else:
                new_list.insert(len(new_list), item)
    elif sortby:
        for item in text_list:
            if sortby in item.lower():
                new_list.append(item)
    if not new_list:
        screens["main"].clear()
        screens["main"].addstr(0, 0, f"No {sortby}s found", colors["highlight"])
        screens["main"].refresh()
        time.sleep(0.5)
        screens["main"].clear()
        return text_list
    return new_list


def cast():
    return

def simple_input(menu):
    pos = 0
    print_list(menu, 1)
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            pos = select(menu, key, pos)
            if not pos:
                pos = 0
        elif key == ord("e"):
            return menu[pos] 
        elif key == ord("q"):
            return None

def inps():
    global list_pos
    pos = 0
    alert_list = 0
    screens["main"].clear()
    while not alert_list:
        alert_list, alert_details, alert_link = get_alert(None)
    cache_list = alert_list
    print_list(alert_list, 1)
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            if not alert_list:
                continue
            pos = select(alert_list, key, pos)
            if not pos:
                pos = 0
        elif key == ord("e"):
            if not alert_list:
                continue
            examine(alert_details, pos)
            screens["main"].clear()
            print_list(alert_list, 1)
        elif key == ord("S"):
            if not list_pos:
                alert_list = cache_list
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: None    ")
                screens["top"].refresh()
            else:
                alert_list = sort_list(cache_list, None, None, None, sorting_phrases[list_pos - 1])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+sorting_phrases[list_pos - 1]+"   ")
                screens["top"].refresh()
           
            list_pos += 1
            if list_pos - 1== len(sorting_phrases):
                list_pos = 0
            screens["main"].clear()
            print_list(alert_list, 1) 
        elif key == ord("R"):
            screens["source"].clear()
            screens["source"].refresh()
            get_alert(None)
            print_list(alert_list, 1)
        elif key == ord("C"):
            config()
            screens["main"].clear()
            get_alert(None)
            print_list(alert_list, 1)
        elif key == ord("!"):
            if parameters["bind 1"] != "none":
                alert_list = sort_list(cache_list, None, None, None, parameters["bind 1"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 1"]+"  ")
                screens["top"].refresh()
                list_pos = 0
            screens["main"].clear()
            print_list(alert_list, 1)
        elif key == ord("@"):
            if parameters["bind 2"] != "none":
                alert_list = sort_list(cache_list, None, None, None, parameters["bind 2"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 2"]+"  ")
                screens["top"].refresh()
                list_pos = 0
            screens["main"].clear()
            print_list(alert_list, 1)
        elif key == ord("#"):
            if parameters["bind 3"] != "none":
                alert_list = sort_list(cache_list, None, None, None, parameters["bind 3"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 3"]+"  ")
                screens["top"].refresh()
                list_pos = 0
            screens["main"].clear()
            print_list(alert_list, 1)
               
        elif key == ord('\x1b'):
            exit()

def select(listy, key, pos):
    if key == ord("s"):
        pos += 1
        if pos >= len(listy):
            pos = len(listy) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos < 0:
            pos = 0
            return
        back = -1
    for event, type in weather_types.items():
        if event in listy[pos - back].lower():
            prevcolor = colors[type]
            break
        else:
            prevcolor = colors["wind"]
    for item in intense:
        if item in listy[pos - back].lower():
            prevcolor = colors["bad"]
            break
    if len(listy) > 1:
        screens["main"].addstr(pos + offset - back, 0, listy[pos - back], prevcolor)
    screens["main"].addstr(pos + offset, 0, listy[pos], colors["highlight"])
    return pos
    
def examine(listy, pos):
    screens["main"].clear()
    screens["main"].refresh()
    print_text(listy[pos], 1)
    while True:
        key = screens["main"].getch()
        if key == ord("q"):
            break
def cleanfiles(param):
    to_rm = []
    count = 0
    for item in os.listdir():
        if "issued" in item:
            to_rm.append(item)
            count += 1
    print(f"this will remove all cached files ({count} files)")
    inp = input("type yes to continue\n(clean up)>>> ")
    if "y" in inp and item:
        for item in to_rm:
            print(f"removing {item}")
            os.remove(item)
    print("back to shell...")

def helpy(param):
    print("\nalert (state): gets alerts for the specified state, if no state is specified, then the default is used.")
    print("clean: removed all HTML files other than alerts.html and past_alerts.html")
    print("set-default: opens the configuration tool")
    print("debug: prints the values of in-use parameters")
    print("help: what do you think?")
    cmd_list = {"alert": get_upd, "cast": cast, "help": helpy, "set-default":config, "debug": debug, "clean": cleanfiles}

def paraupd():
    with open(f"{conf_path}/parameters.conf", "w") as file:
        for key, value in parameters.items():
            file.write(f"{key}={value}\n")

def get_input():
    inp = screens["text"].edit().strip()
    return inp

def debug(param):
    for key, value in parameters.items():
        print(f"{key}={value}")

def config():
    cache = None
    screens["source"].clear()
    screens["top"].clear()
    screens["source"].refresh()
    phrase = "You have opened the config tool. Please select one of these options to configure:"
    screens["top"].addstr(0, 0, phrase, colors["highlight"])
    screens["top"].refresh()
    while True:
        menu = []
        for name, val in parameters.items():
            menu.append(f"{name} > {val}")
        key = simple_input(menu)
        if not key:
            screens["top"].clear()
            screens["top"].refresh()
            screens["main"].clear()
            screens["main"].refresh()
            return 
        key, cache = key.split(" > ")
        screens["main"].clear()
        screens["main"].refresh()
        phrase = f"Selected: {key}\nNew value:"
        print_text(phrase, 1)
        inp = get_input()
        screens["box"].clear()
        screens["box"].refresh()
        screens["source"].clear()
        screens["source"].refresh()
        parameters[key] = inp
        screens["top"].addstr(0, 0, f"updated {inp}. New value: {parameters[key]}", colors["highlight"])
        screens["top"].refresh()
        time.sleep(0.5)
        screens["top"].clear()
        screens["top"].refresh()
        paraupd()
        break
        
def timer():
    global fetch_time, done
    fetch_time = 0
    while True:
        t.sleep(1)
        fetch_time += 1
        if done:
            break

def get_alert(param):
    screens["top"].addstr(0, 0, "getting data...")
    screens["top"].refresh()
    if param:
        state_cache = parameters['state']
        parameters['state'] = param.upper()
    alert_list = []
    alert_details = []
    alert_link = {}
    try:
        count = 1
        done = 0
        y = 1
        weatherdata = requests.get(url+parameters['state'].upper())
        errors = weatherdata.raise_for_status()
        data = weatherdata.json()
        alert_data = data.get("features", [])
        if not alert_data:
            screens["main"].addstr(y, 0, f"No alerts for {parameters['state']}, YAYYYY :DDD")
            screens["main"].addstr(y + 1, 0, f"Shift+R to refresh")
            screens["main"].addstr(y + 2, 0, f"Shift+C for config")
            screens["main"].refresh()
            while True:
                key = screens["main"].getch()
                if key == ord("R"):
                    return 0, 0, 0
                elif key == ord("C"):
                    config()
                    return 0, 0, 0                       
        else:
            screens["top"].clear()
            msg = f"{len(alert_data)} Alerts for {parameters['state']}"
            screens["top"].addstr(0, 0, msg)
        screens["top"].addstr(0, width - width // 2, "Shift+C for config")
        screens["top"].addstr(0, width - width // 4 - (width // 10),"Shift+R to update")
        screens["top"].addstr(0, width - width // 5,"Shift+S to sort")
        screens["top"].refresh()
        y += 1
        for alert in alert_data:
            properties = alert.get("properties", {})
            event = properties.get("event", "unknown event")
            headline = properties.get("headline", "no headline")
            details = properties.get("description", "no description")
            effective = properties.get("effective")
            if parameters["county"] in details.lower():
                headline = "In County>>> " + headline
            nearby = ""
            count = 0
            for direction, abbr  in directions.items():
                if parameters[direction] in details.lower():
                    nearby += f"{abbr}:"
                    count += 1
            if nearby:
                nearby += ">>>"
                if ">>>" in headline:
                    cache, headline = headline.split(">>>")
                if count > 2:
                    nearby = "Large Area>>>"
                headline = nearby + headline
            if parameters["center"] in details.lower():
                if ">>>" in headline:
                    cache, headline = headline.split(">>>")
                headline = "NEARBY>>> " + headline

            if effective:
                time = datetime.fromisoformat(effective.rstrip('Z'))
                time = (time.month, time.day, time.hour, time.minute)
            if not effective:
                time = "Unknown time"
            alrhead = f"{headline}"
            alrmore = f"{event}\n{details}"
            alert_details.append(alrmore)
            alert_list.append(alrhead)
            alert_link.update({alrhead: alrmore})
        if param:
            parameters['state'] = state_cache
    except requests.exceptions.RequestException as e:
        if "400" in str(e):
            msg = f"ERROR GETTING ALERT DATA: 001\nThis error is caused by bad formatting for the state parameter or it doesnt exist\nYou can edit the config file @{conf_path}"
            print_text(msg, 1)
        elif "Temporary failure in name resolution" in str(e):
            msg = f"ERROR GETTING ALERT DATA: 002\nIt seems that your device cannot connect to the NOAA website. Check your internet, wifi, or ethernet\n{url+parameters['state']}"
            print_text(msg, 1)
        else:
            msg = f"ERROR GETTING ALERT DATA (GENERAL FAILURE):\n{e}"
            print_text(msg, 1)
        screens["main"].addstr(y + 5, 0, f"Shift+R to retry")
        screens["main"].addstr(y + 6, 0, f"Shift+C for config")
        screens["main"].refresh()
        while True:
            key = screens["main"].getch()
            if key == ord("R"):
                return 0, 0, 0
            elif key == ord("C"):
                config()
                return 0, 0, 0           
        if param:
            parameters['state'] = state_cache
        time.sleep(0.5)
    return alert_list, alert_details, alert_link
    
def print_text(string, y):
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


def print_list(text_list, y):
    color = None
    to_print = []
    for item in text_list:
        to_print.append(item)
    for item in text_list:
        if y >= height - 5:
            break
        for event, type in weather_types.items():
            if event in item.lower():
                color = colors[type]
                break
        for event in intense:
            if event in item.lower():
                color = colors["bad"]
                break
        if not color:		
            screens["main"].addstr(y, 0, item)
        else:
            screens["main"].addstr(y, 0, item, color)
			
        y += 1
    screens["main"].refresh()

def emergency(event, headline, details, effective):
    while True:
        print(f"********{event} ALERT FOR {parameters['county']}**************")
        print(f"********{event} ALERT FOR {parameters['county']}**************")
        print(f"\n{headline}\n{details}\n")
        print(f"********{event} ALERT FOR {parameters['county']}**************")
        print(f"********{event} ALERT FOR {parameters['county']}**************")
        inp = input("\nPLEASE TYPE 'yes' TO ACKNOWLEDGE\n>>> ")
        if "y" in inp:
            break




wrapper(main)
done = 1


