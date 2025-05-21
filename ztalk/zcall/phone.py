
import threading
import curses
import socket as netcom
import os
import sys
import wave
import time
import subprocess
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
from curses import wrapper
from curses.textpad import Textbox

ip = "0.0.0.0"
mode = "looks"
port = 49494
autoconn = "false"
username = "none"
volume = 5
userstat = "none"
conf_path = "/etc/zcall"

stop = False

"""settings for audio, do not change probably"""
duration = "1"
smpl_rt = "44100"
audio_cache = "iotmp.wav"

attrs = {"ipaddr": ip, "autoconnect": autoconn,"mode": mode, "username": username, "volume": volume, "config path": conf_path}

modes = {"looks": 1, "performance": 0, "stutter": 2}

server = netcom.socket(ipv4, tcp)
def main(stdscr):
    global height, width, HL_1, HL_2
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.refresh()

    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    HL_1 = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
    HL_2 = curses.color_pair(2)

    usr_inp = curses.newwin(1, width // 6, height - 1, 0)
    tbox = Textbox(usr_inp)
    actv_usr_win = curses.newwin(height - 2, width // 6, 0, width - (width // 6))
    vol_win = curses.newwin(height - 2, width // 10, 0, 0)


    all_screens = {"main": stdscr, "audio": vol_win, "users": actv_usr_win, "text box": usr_inp}
    autoconfig(all_screens, usr_inp, tbox)
    #server.connect((ip, port))
    iothread = threading.Thread(target=iocache, args=(server, volume,))
    iorecv = threading.Thread(target=call_recv, args=(server, volume,))
    iothread.start()
    timer(10)
    stop = True
    iosend.join()

def call_recv(server, volume):
    return

def iocache(server, volume):
    global stop
    while True:
        if stop:
            break
        subprocess.run([
        "arecord",
        "-d", duration,
        "f", "S16_LE",
        "-r", smpl_rt,
        "-c", "1",
        audio_cache
        ])

        with wave.open(f"{conf_path}/{audio_cache}", "rb") as file:
            file.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
        log(f"{str(len(audio))}\n")

def call_send():
    return

def timer(sleep_time):
    i = 0
    while True:
        time.sleep(1)
        i += 1
        if i == sleep_time:
            break
def autoconfig(all_screens, usr_inp, tbox):
    global attrs
    try:
        if "false" in autoconn:
            manconfig(all_screens, usr_inp, tbox)
        else:
            with open(f"{conf_path}/phone.conf", "r") as file:
                attr_load = file.readlines()
                for item in attr_load:
                    attr, val = item.split("=")
                    attrs[attr.strip()] = val.strip()
    except Exception as e:
        os.makedirs(conf_path, exist_ok=True)
        errlog(f"{e}\n")
        manconfig(all_screens, usr_inp, tbox)

def errlog(err):
    with open(f"{conf_path}/error_log.txt", "a") as file:
        file.write(err)

def print_three(stdscr, msg1, msg2, msg3, y , x, center):
    if center:
        stdscr.addstr(y // 3, x // 2 - (len(msg1) // 2), msg1, HL_1)
        stdscr.addstr(y // 3 + 1, x // 2 - (len(msg2) // 2), msg2, HL_1)
        stdscr.addstr(y // 3 + 2, x // 2 - (len(msg3) // 2), msg3, HL_2)
    else:
        stdscr.addstr(y, x, msg1, HL_1)
        stdscr.addstr(y, x, msg2, HL_1)
        stdscr.addstr(y, x, msg3, HL_2)

    stdscr.refresh()

def notrase(win, text, x, y, yplus):
    num = 0
    for i in text:
        win.addstr(y + yplus, x + num, " ", curses.COLOR_BLACK)
        num += 1
    win.refresh()

def get_inp(tbox, usr_inp):
    result = tbox.edit().strip()
    if result:
        usr_inp.clear()
        usr_inp.refresh()
        return result

def manconfig(all_screens, usr_inp, tbox):
    global ip, username, userstat
    msg1 = "It looks like this is your first time using this app, lets go through and configure your settings before you continue."
    msg2 = "First lets set the IP of the server your connecting to."
    msg3 = "Type in the Server IP Address:"
    print_three(all_screens["main"], msg1, msg2, msg3, height, width, 1)
    ip = get_inp(tbox, usr_inp)
    notrase(all_screens["main"], msg1, width // 2 - (len(msg1) // 2), height // 3, 0)
    notrase(all_screens["main"], msg2, width // 2 - (len(msg2) // 2), height // 3, 1)
    notrase(all_screens["main"], msg3, width // 2 - (len(msg3) // 2), height // 3, 2)
    msg1 = "Next lets get the name you would like to be indentified by"
    msg2 = "The length of your username is limited to 30 chars"
    msg3 = "Enter your username."
    while True:
        print_three(all_screens["main"], msg1, msg2, msg3, height, width, 1)
        username = get_inp(tbox, usr_inp)
        notrase(all_screens["main"], msg1, width // 2 - (len(msg1) // 2), height // 3, 0)
        notrase(all_screens["main"], msg2, width // 2 - (len(msg2) // 2), height // 3, 1)
        notrase(all_screens["main"], msg3, width // 2 - (len(msg3) // 2), height // 3, 2)
        if len(username) <= 30:
            break
        else:
            msg1 = "username exceeded limit"
            msg2 = "username exceeded limit"
            msg3 = "username exceeded limit"

    notrase(all_screens["main"], msg1, width // 2 - (len(msg1) // 2), height // 3, 0)
    notrase(all_screens["main"], msg2, width // 2 - (len(msg2) // 2), height // 3, 1)
    notrase(all_screens["main"], msg3, width // 2 - (len(msg3) // 2), height // 3, 2)
    msg1 = "Would you like to set a status? (yes or no)"
    all_screens["main"].addstr(height // 2, width // 2 - (len(msg1) // 2), msg1, HL_2)
    all_screens["main"].refresh()
    do_stat = get_inp(tbox, usr_inp)
    if "y" in do_stat:
        while True:
            notrase(all_screens["main"], msg1, width // 2, height // 2, 0)
            msg1 = "Please enter your status. (60 char limit)"
            all_screens["main"].addstr(height // 2, width // 2 - (len(msg1) // 2), msg1, HL_2)
            all_screens.refresh()
            userstat = get_inp(tbox, usr_inp)
            if len(userstat) <= 60:
                break
            else:
                msg1 = "status exceeded limit"
        notrase(all_screens["main"], msg1, width // 2, height // 2, msg1, 0)
    all_screens["main"].clear()
    all_screens["main"].refresh()
    msg1 = "Writing to file, please wait..."
    all_screens["main"].addstr(height // 2, width // 2 - (len(msg1) // 2), msg1, HL_2)
    all_screens["main"].refresh()
    time.sleep(modes[mode])
    with open(f"{conf_path}/phone.conf", "w") as file:
        for item, val in attrs.items():
            file.write(f"{item} = {val}\n")
    all_screens["main"].clear()
    msg1 = "Moving to shell..."
    all_screens["main"].addstr(height // 2, width // 2 - (len(msg1) // 2), msg1, HL_2)
    all_screens["main"].refresh()
    time.sleep(modes[mode])
    all_screens["main"].clear()
    all_screens["main"].refresh()
wrapper(main)
