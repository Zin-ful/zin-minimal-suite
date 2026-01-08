import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
import subprocess as proc
import time
import datetime

curusr = os.path.expanduser("~")
conf_path = curusr+"/.zinapp/homescreen"
screens = {}
apps = {}
nametopath = {}
applist = []
offset = 1
pos = 0
highlight = None
timecolor = None
recent_app = ""
done = 0
status_bar = None
wait = 50
remaining = "finding"
bar = ""

user = proc.run("whoami", capture_output=True, text=True)
user = user.stdout.strip()



if ".zinapp" not in os.listdir(curusr):
	os.makedirs(conf_path, exist_ok=True)

if "homescreen" not in os.listdir(curusr+"/.zinapp"):
	os.makedirs(conf_path, exist_ok=True)

if "apps.conf" not in os.listdir(conf_path):
	with open(f"{conf_path}/apps.conf", "w") as file:
		file.write("")

def main(stdscr):
    global screens, bar, height, width, highlight, timecolor, status_bar
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    timecolor = curses.color_pair(2)
    stdscr.clear()
    stdscr.refresh()
    top_win = curses.newwin(0, width, 0, 0)
    main_win = curses.newwin(height - 5, width, 2, 0)
    main_win.clear()
    main_win.refresh()
    screens.update({"source": stdscr})
    screens.update({"main": main_win})
    screens.update({"top": top_win})
    i = 0
    while i != width - 1:
        bar += " "
        i += 1
    status_bar = task.Thread(target=updatetop, args=[screens,])
    status_bar.start()
    batt_status = task.Thread(target=get_batt_time)
    batt_status.start()
    getapps()
    listapps(screens)
    inps(screens)

def get_batt_time():
    global remaining
    temp = get_batt()
    while True:
        if temp != get_batt():
            break

    end = 1
    start = get_batt()
    count = 0
    while not done:
        while get_batt() > start - end:
            time.sleep(1)
            count += 1
        per_min = (start - get_batt()) / (count / 60)
        remaining = round(get_batt() / per_min, 3)
        total_time = 100 / per_min
        save(per_min)

def get_batt():
    batteries = []
    sys_path = "/sys/class/power_supply/" 
    for item in os.listdir(sys_path):
        if item.startswith('BAT'):
            battery_path = os.path.join(sys_path, item)
            capacity_file = os.path.join(battery_path, "capacity")
            if os.path.exists(capacity_file):
                try:
                    with open(capacity_file, "r") as file:
                        batteries.append(int(file.read().strip()))
                except (ValueError, IOError):
                    continue
    if batteries:
        return round_list(batteries, len(batteries))

    return "No batt found"

def save(data):
    with open(conf_path+"/battery_rate", "w") as file:
        file.write(str(data))

def round_list(list1, length):
    total = 0
    for item in list1:
        total += item
    return item / length

def updatetop(screens):
    while not done:
        screens["top"].addstr(0, 0, bar, timecolor)
        screens["top"].addstr(0, 4, f"{user}: {recent_app.strip()}", timecolor)
        now = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        if int(time.strftime("%H", time.localtime())) > 12:
            now += " PM"
        else:
            now += " AM"
        screens["top"].addstr(0, (width // 2) - (len(now) // 2), now, timecolor)
        screens["top"].addstr(0, width // 2 + width // 4, f"{str(get_batt())}%" + f" - {remaining} minutes left", timecolor)         
        screens["top"].refresh()
        time.sleep(20)

def inps(screens):
    global done, status_bar, recent_app, height, width, pos
    while True:
        inp = screens["main"].getch()
        if not applist:
            screens["main"].addstr(1, 0, "No apps found, add to /etc/homescreen/apps.conf")
            screens["main"].addstr(2, 0, "Format to add: /path/to/app/from/exec:Name of app")
            continue
        if inp == ord("e"):
            apprun = applist[pos]
            apprun = nametopath[apprun]
            apptype = apps[apprun]
            done = 1
            screens["source"].clear()
            screens["source"].refresh()
            time.sleep(0.1)
            proc.run([apptype, apprun])
            time.sleep(0.1)
            screens["source"].clear()
            screens["source"].refresh()
            screens["main"].clear()
            screens["main"].refresh()
            listapps(screens)
            done = 0
            recent_app = applist[pos]
            j = 0
            pos = 0

        elif inp == ord("w") or inp == ord("s"):
            select(inp, screens)
        elif inp == ord("R"):
            screens["source"].clear()
            screens["source"].refresh()
            screens["top"].clear()
            screens["top"].refresh()
            screens["main"].clear()
            screens["main"].refresh()
            j = 0
            while j != width - 1:
                screens["top"].addstr(0, j, " ", timecolor)
                j += 1
            listapps(screens)
            pos = 0
def listapps(screens):
    i = 0
    for item in applist:
        time.sleep(0.05)
        screens["main"].addstr(offset + i, 0, item)
        screens["main"].refresh()
        i += 1

def select(key, screens):
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
    screens["main"].addstr(pos + offset, 0, applist[pos], highlight)

def getapps():
    global apps, applist
    with open(f"{conf_path}/apps.conf", "r") as file:
        loadapps = file.readlines()
        for item in loadapps:
            path, name = item.split(":")
            if ".py" in path:
                style = "/bin/python3"
            else:
                style = "/bin/bash"
            applist.append(name)
            nametopath.update({name: path})
            apps.update({path: style})


if "battery_rate" in os.listdir(conf_path):
    with open(conf_path+"/battery_rate", "r") as file:
        rate = float(file.read())
        remaining = round(get_batt() / rate, 3)



wrapper(main)
