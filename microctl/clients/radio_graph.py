import os
import curses
from curses import wrapper
from curses.textpad import Textbox
import time
import datetime
import serial
import random

offset = 1
pos = 0
high = 0
low = 1000
avg_temp = [0]
avg_hum = []
colors = {}
screens = {}

def main(stdscr):
    global height, width, high, low
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
    timec = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
    warn = curses.color_pair(3)
    colors.update({"time":timec})
    colors.update({"hl":highlight})
    colors.update({"warn": warn})
    graph_win = curses.newwin(50, width - (width // 8) + 2, height // 10 - 1, 10)
    screens.update({"graph":graph_win})
    screens.update({"src": stdscr})
    stdscr.clear()
    stdscr.refresh()
    while True:
        temperature, humidity, pressure, rssi, snr = get_temp()
        if not pressure:
            continue
        if float(str(temperature).strip()) > high:
            high = float(str(temperature).strip())
        elif float(str(temperature).strip()) < low:
            low = float(str(temperature).strip())
        avg_temp.append(float(str(temperature).strip()))
        graph(humidity, pressure, rssi, snr)
        time.sleep(0.1)


def test_temp():
    test_list = ["Lost connection to transmistter", "Invalid data format", "Battery Low", "Wind speed lost", "Temperatures approaching low threshhold", "Temperatures approaching high threshhold"]
    if random.randint(0, 10) == 10:
        data = test_list[random.randint(0, len(test_list) - 1)]
        display_message(data, screens["src"])
    temperature = float(random.randint(70, 77))
    humidity = str(random.randint(55, 58)) + "%"
    pressure = str(random.randint(1000, 1015)) + "mb"
    rssi = "-" + str(random.randint(30, 60)) + "db"
    snr = "-" + str(random.randint(20, 40)) + "db"
    return temperature, humidity, pressure, rssi, snr

def get_temp():
    try:
        data = ser.readline()
        ser.write("ack\n".encode("utf-8"))
        data = data.decode("utf-8")
        if data[0] == "!":
            display_message(data.strip("!"), screens["src"])
            return 0, 0, 0, 0, 0
        temperature, humidity, pressure = data.split(" ", 2)
        temperature = str(float(temperature) * 1.8 + 42)
        rssi, snr = data.strip("#").split(" ", 1)
        return temperature, humidity, pressure, rssi, snr
    except Exception as e:
        display_message(str(e), screens["src"])
        return 0, 0, 0, 0, 0

def display_message(msg, screen):
    screen.addstr(0, 0, msg, colors["warn"])
    screen.refresh()
    time.sleep(1)
    #ser.write("!")
    clear = ""
    for item in msg:
        clear += " "
    screen.addstr(0, 0, clear)
    screen.refresh()

def display_misc(rssi, snr, screen, hum, pres):
    screen.addstr(0, (width - width // 3) - (len(rssi) + len(snr)) // 2, f"{rssi} {snr}")
    screen.addstr(1, (width - width // 3) - (len(str(high)) + len(str(low))) // 2, f"High: {high}f Low: {low}f")
    screen.addstr(2, (width - width // 3) - (len(str(high)) + len(str(low))) // 2, f"Humidity: {hum}")
    screen.addstr(3, (width - width // 3) - (len(str(high)) + len(str(low))) // 2, f"Pressure: {pres}")

def temp_to_row(temp, min_temp, max_temp, height):
    if max_temp == min_temp:
        return height - 1  # avoid divide by zero
    normalized = (temp - min_temp) / (max_temp - min_temp)
    return round((1 - normalized) * (height - 1))


def graph(hum, pres, rssi, snr):
    screen = screens["graph"]
    y, x = screen.getmaxyx()
    screen.clear()
    graph_height = y - 2
    graph_width = x - 3
    if len(avg_temp) >= graph_width:
        avg_temp.pop(1)
    min_temp = min(avg_temp)
    max_temp = max(avg_temp)
    j = 0
    temp = 100
    while j < graph_height:
        i = 2
        while i < graph_width:
            i += 1
            screen.addstr(j, i, " ")
        j += 1

    temp_list = []
    i = 2
    last_row = None

    for temp in avg_temp:
        row = temp_to_row(temp, min_temp, max_temp, graph_height)

        # plot point
        screen.addstr(row, i, "█", colors["time"])

        # optional: draw a vertical connection
        if last_row is not None:
            step = 1 if row > last_row else -1
            for r in range(last_row, row, step):
                screen.addstr(r, i, "│")

        last_row = row
        i += 1

        if i >= graph_width:
            break

    for j in range(graph_height):
        temp_label = int(
            max_temp - (j / graph_height) * (max_temp - min_temp)
        )
        if temp_label % 2 == 0 and temp_label not in temp_list:
            temp_list.append(temp_label)
            screen.addstr(j, 0, f"{temp_label:>3}", colors["hl"])
    display_misc(rssi, snr, screens["src"], hum, pres)
    screen.refresh()
#    time.sleep(5)

ser = serial.Serial('/dev/serial0', 9600)
wrapper(main)

