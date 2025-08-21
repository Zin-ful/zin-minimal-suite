#!/usr/bin/env python3

import requests
import json
import threading
import os
from datetime import datetime
import sys
import time as t
import curses
from curses import wrapper
from curses.textpad import Textbox

conf_path = "/etc/weathertool"
if "weathertool" not in os.listdir("/etc"):
    os.makedirs(conf_path, exist_ok=True)

print("Tool Version: 1.3\n")

wait_time = 120 #seconds
wait_time_err = 60
wait_time_noalert = 1800
silent = 1
url = "https://api.weather.gov/alerts/active?area="
name = ""
state = "TX"
county = "none"
alert_list = []
alert_details = []
alert_link = {}
screens = {}
colors = {}
water = ["water", "rain", "flood", "fog", "hydro"]
storm = ["spark", "light", "thunder", "storm", "wind"]
fire = ["heat", "dry"]
intense = ["catastrophic", "blizzard", "fire", "tornado", "hurri", "typhoon"]

pickcolor = [water, storm, fire, intense]

fetch_cmd = ["curl", "-s", url]
pos = 0
offset = 1
parameters = {"wait_time": wait_time, "wait_time_noalert": wait_time_noalert, "wait_time_err": wait_time_err, "silent": silent, "state": state, "county": county}

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
    global height, width, colors, default, screens, pickcolor
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    highlight = curses.color_pair(1)
    wet = curses.color_pair(2)
    spark = curses.color_pair(3)
    heat = curses.color_pair(4)
    bad = curses.color_pair(5)
    default = curses.color_pair(6)
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
    colors.update({"highlight": highlight, "water": wet, "spark": spark, "heat": heat, "catastrophic": bad})
    get_alert(screens, colors, None)
    print_list(screens, colors, alert_list, 1)
    inps(screens, colors)
def cast():
    return

def inps(screens, colors):
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            select(screens, colors, key)
        elif key == ord("e"):
            examine(screens, colors)
            screens["main"].clear()
            print_list(screens, colors, alert_list, 1)
        elif key == ord("R"):
            screens["source"].clear()
            get_alert(screens, colors, None)
            print_list(screens, colors, alert_list, 1)
        elif key == ord("C"):
            config(screens, colors)
            screens["main"].clear()
            get_alert(screens, colors, None)
            print_list(screens, colors, alert_list, 1)
        elif key == ord('\x1b'):
            exit()
def select(screens, colors, key):
    global pos
    if key == ord("s"):
        pos += 1
        if pos >= len(alert_list):
            pos = len(alert_list) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    for item in pickcolor:
        for content in item:
            if content.lower() in alert_list[pos - back].lower():
                prevcolor = colors[item[0]]
                break
            else:
                prevcolor = default
    screens["main"].addstr(pos + offset - back, 0, alert_list[pos - back], prevcolor)
    screens["main"].addstr(pos + offset, 0, alert_list[pos], colors["highlight"])

def examine(screens, colors):
    screens["main"].clear()
    screens["main"].refresh()
    print_text(screens, colors, alert_details[pos], 1)
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
def debug(param):
    for key, value in parameters.items():
        print(f"{key}={value}")
def config(screens, colors):
    global parameters
    inp2 = 0
    cache = None
    screens["source"].clear()
    screens["source"].refresh()
    phrase = "You have opened the config tool. Please select one of these options to configure:"
    screens["main"].addstr(1, width // 2 - len(phrase), phrase, colors["highlight"])
    while True:
        phrase = f"wait_time (webupdater) - the amount of time the auto-updater waits before making a new request Value: {parameters['wait_time']}"
        print_text(screens, colors, phrase, 2)
        phrase = f"wait_time_noalert (webupdater) - the amount of time after no alerts were found that the updater waits before making a new request Value: {parameters['wait_time_noalert']}"
        print_text(screens, colors, phrase, 4)
        phrase = f"wait_time_err (webupdater) - the amount of time the updater waits after getting an error before making a new request. Value: {parameters['wait_time_err']}"
        print_text(screens, colors, phrase, 6)
        phrase = f"url (not able to be changed)- the URL that the program will request data from (json formatted). Value: {url}"
        print_text(screens, colors, phrase, 8)
        phrase = f"state - the state in which you want alerts from. Value: {parameters['state']}"
        print_text(screens, colors, phrase, 10)
        phrase = f"county - setting the county will force open a browser if theres an alert found for your county. Value: {parameters['county']}\n**If no browser exists, it will take over the command-line and will force you to confirm that youve seen it."
        print_text(screens, colors, phrase, 12)
        inp = screens["text"].edit().strip()
        if inp:
            screens["box"].clear()
            screens["box"].refresh()
            for key, value in parameters.items():
                if inp.lower() == key:
                    cache = key
                    screens["main"].clear()
                    screens["main"].refresh()
                    phrase = f"Selected: {key}\nNew value:"
                    print_text(screens, colors, phrase, 1)
        if not cache:
            phrase = f"Sorry, that phrase is invalid. Choose a proper parameter like 'state' "
            print_text(screens, colors, phrase, 4)
            break
        inp = screens["text"].edit().strip()
        if inp:
            key = cache
            screens["box"].clear()
            screens["box"].refresh()
            if key == "county" or key == "state":
                if key == "state":
                    inp = inp.upper()
                else:
                    try:
                        inp2 = int(inp)
                    except:
                        print("Numbers only please.")
                        continue
        screens["source"].clear()
        screens["source"].refresh()
        if not inp2:
            parameters[key] = str(inp)
        else:
            parameters[key] = str(inp2)
        screens["main"].addstr(height // 2, 0, f"updated {inp}. New value: {parameters[key]}", colors["highlight"])
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

def get_alert(screens, colors, param):
    global done, alert_details, alert_list, alert_link
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
        time_thread = threading.Thread(target=timer)
        time_thread.start()
        weatherdata = requests.get(url+parameters['state'].upper())
        errors = weatherdata.raise_for_status()
        data = weatherdata.json()
        alert_data = data.get("features", [])
        done = 1
        time_thread.join()
        if not alert_data:
            screens["main"].addstr(y, 0, f"NO ALERTS FOR {parameters['state']}, YAYYYY :DDD")
            screens["main"].refresh()
            while True:
                key = screens["main"].getch()
                if key == ord('\x1b'):
                    done = 1
                    time_thread.join()
                    exit()
        else:
            screens["top"].addstr(0, width // 2 + width // 4, f"!!{len(alert_data)} ALERTS FOR {parameters['state']} FOUND..")
            screens["top"].refresh()
        y += 1
        for alert in alert_data:
            properties = alert.get("properties", {})
            event = properties.get("event", "unknown event")
            headline = properties.get("headline", "no headline")
            details = properties.get("description", "no description")
            effective = properties.get("effective")
            if effective:
                time = datetime.fromisoformat(effective.rstrip('Z')).strftime('%Y-%m-%d %H:%M %Z')
            if not effective:
                time = "Unknown time"
            alrhead = f"{time}: {headline}"
            alrmore = f"{time}: {event}\n{details}"
            alert_details.append(alrmore)
            alert_list.append(alrhead)
            alert_link.update({alrhead: alrmore})
        if param:
            parameters['state'] = state_cache
        screens["main"].addstr(height - 6, width // 2, f"fetched in: {fetch_time}")
    except requests.exceptions.RequestException as e:
        if "400" in str(e):
            msg = f"*ERROR GETTING ALERT DATA: {e} **THE ERROR YOUVE ENCOUNTERED IS BECAUSE THE STATE IS NOT SET OR IT IS FORMATTED WRONG.***\nEITHER SET IT IN THE CONFIG FILE OR USE THE 'set-default' COMMAND"
            print_text(screens, colors, msg, 1)
        elif "Temporary failure in name resolution" in str(e):
            msg = f"ERROR GETTING ALERT DATA: \n\n{e}\n\n***THE ERROR YOUVE ENCOUNTERED IS BECAUSE THE DEVICE CANNOT REACH THE SPECIFIED URL***\nEITHER THE URL IS INCORRECT, NO LONGER MAINTAINED (INACTIVE), OR THE DEVICE DOES NOT HAVE INTERNET ACCESS/ACCESS TO THIS SPECIFIC URL: \n{url+parameters['state']}"
            print_text(screens, colors, msg, 1)
        else:
            msg = f"ERROR GETTING ALERT DATA:\n{e}"
            print_text(screens, colors, msg, 1)
        if param:
            parameters['state'] = state_cache
        done = 1

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


