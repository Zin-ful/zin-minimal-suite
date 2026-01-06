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
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom

curusr = os.path.expanduser("~")

conf_path = "/.zinapp/weathertool"
if ".zinapp" not in os.listdir(curusr):
	os.mkdir(curusr+"/.zinapp")
if "weathertool" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(curusr + conf_path)

conf_path = curusr + conf_path

print("Tool Version: 2.0\n")

name = ""
state = "TX"
lattlong = "1.000-1.000"
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
connect_to_server = "false"
server_ip = "?.?.?.?"
wait_time = "120"

url = "https://api.weather.gov/alerts/active?area="
times = {}
screens = {}
colors = {}

weather_types = {"surf": "water", "water": "water", "rain": "water", "flood": "water", "fog": "water", "hydro": "water", "wind": "wind", "heat": "heat", "dry":"heat", "fire": "heat", "red flag": "heat", "snow": "cold", "winter": "cold", "freeze": "cold", "frost": "cold", "spark": "spark", "light": "spark", "thunder": "spark", "storm": "spark"}
intense = ["extreme", "severe", "blizzard", "tornado", "hurri", "typhoon", "flood", "surge"]

parameters = {"state": state, "latt/long": lattlong, "county": county, "alternate server": connect_to_server, "server ip": server_ip, "refresh time": wait_time,
"center": center, "west": WT, "east": ET, "south": ST, "north": NT, 
"north east": NE, "south east": SE, "south west": SW, "north west": NW,  
"bind 1": bind_1, "bind 2": bind_2, "bind 3": bind_3}

help_list = [
"Shift+R > Sends a request to update your current alerts with the latest one.",
"If alternate server is true, the server updates based on wait-time)",
"Shift+C > Opens the configuration. The directions (north, west, etc) are nearby locations that will set the map values.",
"Shift+S > Sorts the current alert list by alert type.",
"Shift+Q > Return to previous screen",
"Shift+A > Displays the most recent archived alert",
"Shift+H > Displays the help screen",
"Shift+V > Displays the map",
"Shift+F > Searches alerts for a given phrase",
"binds 1-3 > Custom phrases for sorting, trigged by Shift+1 through 3",
"Latt/Long > Your lattitude and longitude, multiple tools can find this. ",
"Proper syntax is {latt} {long}. Example: 41.14743 -23.46758",
"Center/Directions > 'center' is the town you reside in inside of your county",
"setting this and directions will build a map of alerts.",
"Alt server > If you download and have the srvweather.py file from zin-minimal-suite and",
"start it on a device that you can connect to, enabling this will allow connection to that server",
"instead of weather.gov which can be several times faster as the server"
]

directions = {"center": "????", "north":"????", "south":"????","west":"????", "east":"????", 
"south west":"????", "south east":"????","north west":"????", "north east":"????"}

sorting_phrases = ["warning", "alert", "outlook", "advisory", "watch"]


fetch_cmd = ["curl", "-s", url]
pos = 0
offset = 1
list_pos = 0

connected = 0

port = 49021
server = netcom.socket(ipv4, tcp)

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
    for key, val in directions.items():
        directions[key] = parameters[key]

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
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_BLUE)
    
    highlight = curses.color_pair(1)
    wet = curses.color_pair(2)
    cold = curses.color_pair(7)
    spark = curses.color_pair(3)
    heat = curses.color_pair(4)
    bad = curses.color_pair(5)
    wind = curses.color_pair(6)
    caution = curses.color_pair(8)
    lookout = curses.color_pair(9)
    stdscr.clear()
    stdscr.refresh()

    top_win = curses.newwin(0, width, 0, 0)
    main_win = curses.newwin(height - 2, width, 1, 0)
    help_win = curses.newwin(height - 4, width - 4, 3, 4)
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    map_win = curses.newwin(height - 10, width - 15, 1, 5)
    tbox = Textbox(user_input)
    screens.update({"top": top_win})
    screens.update({"main": main_win})
    screens.update({"box": user_input})
    screens.update({"text": tbox})
    screens.update({"source": stdscr})
    screens.update({"help": help_win})
    screens.update({"map": map_win})
    colors.update({"highlight": highlight, "water": wet, "spark": spark, "heat": heat, 
    "bad": bad, "caution": caution, "lookout": lookout,
    "cold": cold, "wind": wind})
    while True:
        stdscr.clear()
        stdscr.refresh()
        choice = simple_input(["Forecast", "Alerts", "Settings", "Exit"])
        if choice == "Forecast":
            forecast_inps()
        elif choice == "Alerts":
            alert_inps()
        elif choice == "Settings":
            config()
        elif not choice or choice == "Exit":
            exit()

def clear_all():
    for item, screen in screens.items():
        if item == "text":
            continue
        screen.clear()
        screen.refresh()

def init():
    clear_all()
    if parameters["server ip"] == "?.?.?.?":
        print_text("invalid IP address, to connect, configure it. Press C to configure, Q to return with alt server off config", 1)
        while True:
            key = screens["main"].getch()
            if key == ord("C"):
                config()
                return 0
            elif key == ord("Q"):
                parameters["alternate server"] = "false"
                paraupd()
                clear_all()
                return 1
    try:
        server.connect((parameters["server ip"], port))
    except ConnectionRefusedError:
        print_text("Failed to initalize with server.\nEither the server is down\nyour not connected to internet\nor you dont have a direct path to the server (hamachi, wireguard, openvpn, etc)\nPress C to configure, Q to exit with alt server off, or R to retry", 1)
        while True:
            key = screens["main"].getch()
            if key == ord("C"):
                config()
                return 0
            elif key == ord("R"):
                return 0
            elif key == ord("Q"):
                parameters["alternate server"] = "false"
                paraupd()
                return 1
    print_text("connecting", 0)
    screens["main"].refresh()
    time.sleep(0.1)
    server.send(parameters["state"].encode("utf-8"))
    print_text("sending config", 0)
    screens["main"].refresh()
    time.sleep(0.1)
    server.send(parameters["refresh time"].encode("utf-8"))
    server.recv(1)
    print_text("connected to server", 0)
    screens["main"].refresh()
    time.sleep(0.1)
    screens["main"].clear()
    screens["main"].refresh()
    return 1    
    
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
        time.sleep(0.2)
        screens["main"].clear()
        return text_list
    return new_list

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

def map(alert_list, alert_details):
    map_y, map_x = screens["map"].getmaxyx()
    i = 0
    dir_color = {"center": 0, "north west": 0, "north": 0, "north east": 0, "south west": 0, "south": 0, "south east": 0, "east": 0, "west": 0}
    dirs = ["center", "north west", "north", "north east", "south west", "south", "south east", "east", "west"]
    for item in alert_details:
        for dir in dirs:
            if parameters[dir].lower() in item.lower() or parameters[dir].lower() in alert_list[i].lower():
                if "warning" in alert_list[i].lower():
                    dir_color[dir] = colors["bad"]
                elif "advisory" in alert_list[i].lower():
                    dir_color[dir] = colors["caution"]
                elif "watch" in alert_list[i].lower():
                    dir_color[dir] = colors["lookout"]
                else:
                    dir_color[dir] = colors["wind"]

        i += 1       
    screens["map"].clear()
    
    screens["map"].addstr(0, 0, "Red = ")
    screens["map"].addstr(1, 0, "Yellow =")
    screens["map"].addstr(2, 0, "Blue = ")
    screens["map"].addstr(0, len("Red =  "), "Warning", colors["bad"])
    screens["map"].addstr(1, len("Yellow = "), "Advisory", colors["caution"])
    screens["map"].addstr(2, len("Blue =  "), "Watch", colors["lookout"])
    
    
    screens["map"].addstr(map_y // 2, map_x // 2, directions["center"], dir_color["center"])
    screens["map"].addstr((map_y // 7) + 2, (map_x // 6) + 6, directions["north west"], dir_color["north west"])
    screens["map"].addstr((map_y // 7) - 2, map_x // 2, directions["north"], dir_color["north"])
    screens["map"].addstr((map_y // 7) + 2, (map_x - map_x // 6) - 6, directions["north east"], dir_color["north east"])
    screens["map"].addstr((map_y - (map_y // 7)) - 2, (map_x // 6) + 6, directions["south west"], dir_color["south west"])
    screens["map"].addstr((map_y - (map_y // 7)) + 2, map_x // 2, directions["south"], dir_color["south"])
    screens["map"].addstr((map_y - (map_y // 7)) - 2, (map_x - map_x // 6) - 6, directions["south east"], dir_color["south east"])
    screens["map"].addstr(map_y // 2, map_x // 6, directions["west"], dir_color["west"])
    screens["map"].addstr(map_y // 2, map_x - (map_x // 6), directions["east"], dir_color["east"])

    screens["map"].refresh()

def find(alert_list, alert_details):
    screens["source"].clear()
    screens["source"].refresh()
    screens["top"].addstr(0, 0, "Type in the phrase you want to search for:", colors["wind"])
    screens["top"].refresh()
    phrase = screens["text"].edit().strip()
    found = []
    found_list = []
    if phrase:
        i = 0
        for item in alert_details:
            if phrase.lower() in item.lower() or phrase.lower() in alert_list[i].lower():
                found.append(alert_details[i])
                found_list.append(alert_list[i])
            i += 1
    
    clear_all()
    if found:
        pos = 0
        screens["top"].addstr(0, 0, f"'{phrase}' found in {len(found)} alerts:", colors["wind"])
        screens["top"].refresh()
        print_list(found_list, 1)
        y, x = screens["main"].getmaxyx()
        while True:
            key = screens["main"].getch()
            if key == ord("w") or key == ord("s"):
                if len(found_list) > y:
                    i = len(found_list) // 2
                    for i in range(len(found_list) // 2):
                        alert_list_2.append(found_list[i])
                    i = 0
                    for i in range(len(found_list) // 2):
                        alert_list_1.append(found_list[i])
                    if pos >= len(found_list_1):
                        pos = select(found_list_2, key, pos)
                    else:
                        pos = select(found_list_1, key, pos)
                else:        
                    pos = select(found_list, key, pos)
                if not pos:
                    pos = 0
            elif key == ord("e"):
                examine(found, pos)
                screens["main"].clear()
                print_list(found_list, 1)
            elif key == ord("q"):
                break
    else:
        screens["top"].addstr(0, 0, f"'{phrase}' not found in alerts", colors["wind"])
        screens["top"].refresh()
        print_text("Any key to continue", 1)
        screens["main"].getch()
    clear_all()

def alert_inps():
    global connected, list_pos
    pos = 0
    connected = 0
    alert_list = 0
    screens["main"].clear()
    if parameters["alternate server"] != "false":
        while not connected:
            connected = init()
    while not alert_list:
        if parameters["alternate server"] == "false":
            alert_list, alert_details, alert_link = get_alert(None)
        else:
            alert_list, alert_details, alert_link = alt_alert("*")
            
    cache_list = alert_list
    print_list(alert_list, 1)
    y, x = screens["main"].getmaxyx() 
    while True:
        if not connected and parameters["alternate server"] != "false":
            connected = init()
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            if not alert_list:
                continue
            if len(alert_list) > y:
                i = len(alert_list) // 2
                for i in range(len(alert_list) // 2):
                    alert_list_2.append(alert_list[i])
                i = 0
                for i in range(len(alert_list) // 2):
                    alert_list_1.append(alert_list[i])
                if pos >= len(alert_list_1):
                    pos = select(alert_list_2, key, pos)
                else:
                    pos = select(alert_list_1, key, pos)
            else:        
                pos = select(alert_list, key, pos)
            if not pos:
                pos = 0
        elif key == ord("q"):
            list_pos = 0
            return
        elif key == ord("e"):
            if not alert_list:
                continue
            examine(alert_details, pos)
            screens["main"].clear()
            print_list(alert_list, 1)
        elif key == ord("F"):
            find(alert_list, alert_details)
            screens["source"].clear()
            screens["source"].refresh()
            if parameters["alternate server"] == "false":
                alert_list, alert_details, alert_link = get_alert(None)
            else:
                if not connected and parameters["alternate server"] != "false":
                    connected = init()
                alert_list, alert_details, alert_link = alt_alert("*") 
            print_list(alert_list, 1)
        elif key == ord("T"):
            pass #put auto refresh here
        elif key == ord("A"):
            temp_al, temp_ad, temp_ak = archive()
            if temp_al:
                alert_list = temp_al
                alert_details = temp_ad
                alert_link = temp_ak

            print_list(alert_list, 1)
        elif key == ord("V"):
            map(alert_list, alert_details)
            screens["main"].getch()
            screens["map"].clear()
            screens["map"].refresh()
            print_list(alert_list, 1)
        elif key == ord("H"):
            screens["help"].clear()
            i = 0
            for item in help_list:
                if ">" in item:
                    i += 1
                screens["help"].addstr(i, 0, item)
                i += 1
            screens["help"].refresh()
            screens["main"].getch()
            screens["help"].clear()
            screens["help"].refresh()
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
            if parameters["alternate server"] == "false":
                alert_list, alert_details, alert_link = get_alert(None)
            else:
                if not connected and parameters["alternate server"] != "false":
                    connected = init()
                alert_list, alert_details, alert_link = alt_alert("*") 
            print_list(alert_list, 1)

        elif key == ord("C"):
            config()
            screens["main"].clear()
            if parameters["alternate server"] == "false":
                alert_list, alert_details, alert_link = get_alert(None)
            else:
                if not connected and parameters["alternate server"] != "false":
                    connected = init()
                alert_list, alert_details, alert_link = alt_alert(parameters["state"])                   
            print_list(alert_list, 1)

        elif key == ord("!"):
            if parameters["bind 1"] != "????":
                alert_list = sort_list(cache_list, None, None, None, parameters["bind 1"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 1"]+"  ")
                screens["top"].refresh()
                list_pos = 0
                screens["main"].clear()
                print_list(alert_list, 1)

        elif key == ord("@"):
            if parameters["bind 2"] != "????":
                alert_list = sort_list(cache_list, None, None, None, parameters["bind 2"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 2"]+"  ")
                screens["top"].refresh()
                list_pos = 0
                screens["main"].clear()
                print_list(alert_list, 1)

        elif key == ord("#"):
            if parameters["bind 3"] != "????":
                alert_list = sort_list(cache_list, None, None, None, parameters["bind 3"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 3"]+"  ")
                screens["top"].refresh()
                list_pos = 0
                screens["main"].clear()
                print_list(alert_list, 1)
               
        elif key == ord('\x1b'):
            exit()

def forecast_inps():
    global connected, list_pos
    pos = 0
    connected = 0
    forecast_list = 0
    screens["main"].clear()
    if parameters["alternate server"] != "false":
        while not connected:
            connected = init()
    while not forecast_list:
        if parameters["alternate server"] == "false":
            forecast_list, forecast_details, forecast_link = get_forecast(None)
        else:
            forecast_list, forecast_details, forecast_link = alt_alert("*")
            
    cache_list = forecast_list
    print_list(forecast_list, 1)
    y, x = screens["main"].getmaxyx() 
    while True:
        if not connected and parameters["alternate server"] != "false":
            connected = init()
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            if not forecast_list:
                continue
            if len(forecast_list) > y:
                i = len(forecast_list) // 2
                for i in range(len(forecast_list) // 2):
                    forecast_list_2.append(forecast_list[i])
                i = 0
                for i in range(len(forecast_list) // 2):
                    forecast_list_1.append(forecast_list[i])
                if pos >= len(forecast_list_1):
                    pos = select(forecast_list_2, key, pos)
                else:
                    pos = select(forecast_list_1, key, pos)
            else:        
                pos = select(forecast_list, key, pos)
            if not pos:
                pos = 0
        elif key == ord("q"):
            list_pos = 0
            return
        elif key == ord("e"):
            if not forecast_list:
                continue
            examine(forecast_details, pos)
            screens["main"].clear()
            print_list(forecast_list, 1)
        elif key == ord("F"):
            find(forecast_list, forecast_details)
            screens["source"].clear()
            screens["source"].refresh()
            if parameters["alternate server"] == "false":
                forecast_list, forecast_details, alert_link = get_alert(None)
            else:
                if not connected and parameters["alternate server"] != "false":
                    connected = init()
                forecast_list, forecast_details, forecast_link = alt_alert("*") 
            print_list(forecast_list, 1)
        elif key == ord("T"):
            pass #put auto refresh here
        elif key == ord("A"):
            temp_al, temp_ad, temp_ak = archive()
            if temp_al:
                forecast_list = temp_al
                forecast_details = temp_ad
                forecast_link = temp_ak

            print_list(forecast_list, 1)
        elif key == ord("S"):
            if not list_pos:
                forecast_list = cache_list
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: None    ")
                screens["top"].refresh()
            else:
                forecast_list = sort_list(cache_list, None, None, None, sorting_phrases[list_pos - 1])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+forecast_sorting_phrases[list_pos - 1]+"   ")
                screens["top"].refresh()
            list_pos += 1
            if list_pos - 1== len(sorting_phrases):
                list_pos = 0
            screens["main"].clear()
            print_list(forecast_list, 1) 

        elif key == ord("R"):
            screens["source"].clear()
            screens["source"].refresh()
            if parameters["alternate server"] == "false":
                forecast_list, forecast_details, forecast_link = get_forecast(None)
            else:
                if not connected and parameters["alternate server"] != "false":
                    connected = init()
                forecast_list, forecast_details, forecast_link = alt_alert("*") 
            print_list(forecast_list, 1)

        elif key == ord("C"):
            config()
            screens["main"].clear()
            if parameters["alternate server"] == "false":
                forecast_list, forecast_details, forecast_link = get_forecast(None)
            else:
                if not connected and parameters["alternate server"] != "false":
                    connected = init()
                forecast_list, forecast_details, forecast_link = alt_alert(parameters["state"])                   
            print_list(forecast_list, 1)

        elif key == ord("!"):
            if parameters["bind 1"] != "????":
                forecast_list = sort_list(cache_list, None, None, None, parameters["bind 1"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 1"]+"  ")
                screens["top"].refresh()
                list_pos = 0
                screens["main"].clear()
                print_list(forecast_list, 1)

        elif key == ord("@"):
            if parameters["bind 2"] != "????":
                forecast_list = sort_list(cache_list, None, None, None, parameters["bind 2"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 2"]+"  ")
                screens["top"].refresh()
                list_pos = 0
                screens["main"].clear()
                print_list(forecast_list, 1)

        elif key == ord("#"):
            if parameters["bind 3"] != "????":
                forecast_list = sort_list(cache_list, None, None, None, parameters["bind 3"])
                screens["top"].addstr(0, width - (width // 3) * 2, "Sort by: "+parameters["bind 3"]+"  ")
                screens["top"].refresh()
                list_pos = 0
                screens["main"].clear()
                print_list(forecast_list, 1)
               
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
    while True:
        cache = None
        clear_all()
        phrase = "You have opened the config tool. Please select one of these options to configure:"
        screens["top"].addstr(0, 0, phrase, colors["highlight"])
        screens["top"].refresh()
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
        screens["top"].addstr(0, 0, f"updated {inp}. New value: {parameters[key]}      ", colors["highlight"])
        screens["top"].refresh()
        time.sleep(0.3)
        screens["top"].clear()
        screens["top"].refresh()
        paraupd()
        continue
        
def timer():
    global fetch_time, done
    fetch_time = 0
    while True:
        t.sleep(1)
        fetch_time += 1
        if done:
            break

def save(data, mode):
    with open(conf_path+"/archive_alert.txt", mode) as file:
         file.write(data)

def clear_save():
    with open(conf_path+"/archive_alert.txt", "w") as file:
        file.write("")

def load():
    with open(conf_path+"/archive_alert.txt", "r") as file:
        data = file.read()
    return data

def archive_time():
     creation_time = datetime.fromtimestamp(os.path.getctime(conf_path+"/archive_alert.txt"))
     return f"{creation_time.month}-{creation_time.day} {creation_time.hour}:{creation_time.minute}"

def recv_exact(sock, bytes):
    buf = b""
    while len(buf) < bytes:
        chunk = sock.recv(bytes - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed")
        buf += chunk
    return buf

def recv_packet(sock):
    header = b""
    while not header.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Socket closed while reading header")
        header += chunk
    length = int(header.strip())
    return recv_exact(sock, length)

def archive():
    clear_all()
    time.sleep(0.1)
    alert_list = []
    alert_details = []
    alert_link = {}
    y = 1
    if "archive_alert.txt" in os.listdir(conf_path):
        alert_data = load()
    else:
        screens["main"].addstr(y, 0, f"No archive file.")
        screens["main"].addstr(y + 1, 0, f"Shift+R to refresh")
        screens["main"].addstr(y + 2, 0, f"Shift+C for config")
        screens["main"].refresh()
        while True:
            key = screens["main"].getch()
            if key == ord("R"):
                clear_all()
                return 0, 0, 0
            elif key == ord("C"):
                 config()
                 return 0, 0, 0

    if alert_data == "%":
        screens["main"].addstr(y, 0, f"No alerts for {parameters['state']}, YAYYYY :DDD")
        screens["main"].addstr(y + 1, 0, f"Shift+R to refresh")
        screens["main"].addstr(y + 2, 0, f"Shift+C for config")
        screens["main"].refresh()
        while True:
            key = screens["main"].getch()
            if key == ord("R"):
                clear_all()
                return 0, 0, 0
            elif key == ord("C"):
                config()
                return 0, 0, 0
    else:
        if "%" not in alert_data:
            current_time = archive_time()
        else:
            current_time, alert_data = alert_data.split("%", 1)
        all_alerts = []
        i = 0
        while "##" in alert_data:
            alert, alert_data = alert_data.split("##", 1)
            all_alerts.append(alert)
        screens["top"].clear()
        screens["top"].addstr(0, 0, f"{len(all_alerts)} Alerts for {parameters['state']}")
        screens["top"].addstr(0, width - width // 2, f"archived at: {archive_time()}")
        screens["top"].addstr(0, width - width // 4, "Shift+H for help")
        screens["top"].refresh()
        y += 1
        for item in all_alerts:
            headline, event = item.split("@!", 1)
            headline = headline.strip()
            event, details = event.split("!@", 1)
            event = event.strip()
            details = details.strip()
            alrhead = f"{headline}"
            alrmore = f"{event}\n{details}"
            alert_details.append(alrmore)
            alert_list.append(alrhead)
            alert_link.update({alrhead: alrmore})
    return alert_list, alert_details, alert_link

def alt_alert(state):
    global server, connected
    clear_all()
    time.sleep(0.1)
    screens["top"].addstr(0, 0, "getting data...")
    screens["top"].refresh()
    alert_list = []
    alert_details = []
    alert_link = {}
    y = 1
    try:
        sending = 1
        server.send(state.encode("utf-8"))
        sending = 0
        getting = 1
        alert_data = recv_packet(server).decode("utf-8")
    except (ConnectionResetError, ConnectionRefusedError, TimeoutError, BrokenPipeError):
        connected = 0
        if sending:
            print_text("Lost connection to the server during send.\nIts likely you have lost complete connection to the server or it went down.\nPress C for config, R to retry, or Q to swap off the alernative server and back out", 1)
        elif getting:
            print_text("Lost connection to the server during receive.\nIts likely there was a service interruption on your end due to a spotty connection.\nR to try again, C for configuration, or Q to back out and stop using the alt server", 1)
        while True:
            key = screens["main"].getch()
            if key == ord("R"):
                return 0, 0, 0
            elif key == ord("C"):
                config()
                return 0, 0, 0
            elif key == ord("A"):
                return archive()
                
            elif key == ord("Q"):
                parameters["alternate server"] = "false"
                paraupd()
                clear_all()
                return 0, 0, 0
    if alert_data.startswith("%") and alert_data.count("##") == 0:
        screens["main"].addstr(y, 0, f"No alerts for {parameters['state']}, YAYYYY :DDD")
        screens["main"].addstr(y + 1, 0, f"Shift+R to refresh")
        screens["main"].addstr(y + 2, 0, f"Shift+C for config")
        screens["main"].refresh()
        while True:
            key = screens["main"].getch()
            if key == ord("R"):
                clear_all()
                return 0, 0, 0
            elif key == ord("C"):
                config()
                return 0, 0, 0
    else:
        all_alerts = []
        save(alert_data, "w")
        alert_data = load()
        current_time, alert_data = alert_data.split("%", 1)
        i = 0
        while "##" in alert_data:
            alert, alert_data = alert_data.split("##", 1)
            all_alerts.append(alert)

        screens["top"].clear()
        screens["top"].addstr(0, 0, f"{len(all_alerts)} Alerts for {parameters['state']}")
        screens["top"].addstr(0, width - width // 2, current_time)
        screens["top"].addstr(0, width - width // 4, "Shift+H for help")
        screens["top"].refresh()
        y += 1

        for item in all_alerts:
            headline, event = item.split("@!", 1)
            headline = headline.strip()
            event, details = event.split("!@", 1)
            event = event.strip()
            details = details.strip()
            alrhead = f"{headline}"
            alrmore = f"{event}\n{details}"
            alert_details.append(alrmore)
            alert_list.append(alrhead)
            alert_link.update({alrhead: alrmore})
            
    return alert_list, alert_details, alert_link

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
                elif key == ord("A"):
                    return archive()
        current_time = datetime.now().strftime("%m-%d %H:%M")
        screens["top"].clear()
        screens["top"].addstr(0, 0, f"{len(alert_data)} Alerts for {parameters['state']}")
        screens["top"].addstr(0, width - width // 2, current_time)
        screens["top"].addstr(0, width - width // 4, "Shift+H for help")
        screens["top"].refresh()
        y += 1
        clear_save()
        for alert in alert_data:
            properties = alert.get("properties", {})
            event = properties.get("event", "unknown event")
            headline = properties.get("headline", "no headline")
            details = properties.get("description", "no description")
            effective = properties.get("effective")
            save(f"{headline}\n@!\n{event}\n!@\n{details}\n##\n", "a")
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
            elif key == ord("A"):
                return archive()     
        if param:
            parameters['state'] = state_cache
        time.sleep(0.5)
    return alert_list, alert_details, alert_link

def get_forecast(param=None):

    if param:
        state_cache = parameters['state']
        parameters['state'] = param.upper()

    forecast_titles = []
    forecast_details = []
    forecast_link = {}

    try:
        # Expecting parameters["center"] = (lat, lon)
        lat, lon = parameters["latt/long"].split(" ")

        point_url = f"https://api.weather.gov/points/{lat},{lon}"
        point_data = requests.get(point_url)
        point_data.raise_for_status()
        point_json = point_data.json()

        forecast_url = point_json["properties"]["forecast"]

        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_json = forecast_response.json()

        periods = forecast_json["properties"].get("periods", [])

        if not periods:
            return [], [], {}

        for period in periods:
            name = period.get("name", "Unknown period")
            detailed = period.get("detailedForecast", "No forecast text available")

            forecast_titles.append(name)
            forecast_details.append(detailed)
            forecast_link[name] = detailed

    except requests.exceptions.RequestException as e:
        # Let caller handle UI / retry logic
        raise RuntimeError(f"ERROR GETTING FORECAST DATA:\n{e}")

    finally:
        if param:
            parameters['state'] = state_cache

    return forecast_titles, forecast_details, forecast_link


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


