import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
import subprocess as proc
import random

done = 0
screens = {}
colors = {}
pause = 0

curusr = os.path.expanduser("~")
if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "homescreen" not in os.listdir(curusr+"/.zinapp")
    os.mkdir(curusr+"/.zinapp/homescreen")

conf_path = curusr+"/.zinapp/homescreen/"

    
def main(stdscr):
    global bar, height, width
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    one = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    two = curses.color_pair(3)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)
    three = curses.color_pair(4)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
    four = curses.color_pair(5)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    five = curses.color_pair(6)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_CYAN)
    six = curses.color_pair(7)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
    seven = curses.color_pair(8)
    
    stdscr.clear()
    stdscr.refresh()
    colors.update({"1": one})
    colors.update({"2": two})
    colors.update({"3": three})
    colors.update({"4": four})
    colors.update({"5": five})
    colors.update({"6": six})
    colors.update({"7": seven})
    colors.update({"highlight": highlight})
    main_win = curses.newwin(height - 1, width, 2, 0)
    main_win.clear()
    main_win.refresh()
    screens.update({"source": stdscr})
    screens.update({"main": main_win})
    inps()

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

def round_list(list1, length):
    total = 0
    for item in list1:
        total += item
    return item / length

def print_scr(text, y):
    screens["main"].addstr(y, 0, text)
    screens["main"].refresh()



def short_test():
    end = 1
    print_scr(f"(Short) Starting value: {get_batt()}%", 0)
    start = get_batt()
    count = 0
    while True:
        time.sleep(1)
        print_scr(str(count) + f" current percent: {get_batt()}%", 4)
        count += 1
        if get_batt() < start - end:
            break
    per_min = (start - get_batt()) / (count / 60)
    print_scr(f"Test end. Current battery time: {get_batt() / per_min} minutes left", 5)
    print_scr(f"Battery consuption per minute: {per_min}", 6)
    print_scr(f"Total battery time: {100 / per_min}", 7)
    print_scr(f"Current battery percent: {get_batt()}", 8)
    print_scr("Press any button to continue", 9)
    screens["main"].getch()
    
def med_test():
    end = 3
    print_scr(f"(Medium) Starting value: {get_batt()}%", 0)
    start = get_batt()
    count = 0
    while True:
        time.sleep(1)
        print_scr(str(count) + f" current percent: {get_batt()}%", 4)
        count += 1
        if get_batt() < start - end:
            break
    per_min = (start - get_batt()) / (count / 60)
    print_scr(f"Test end. Current battery time: {get_batt() / per_min} minutes left", 5)
    print_scr(f"Battery consuption per minute: {per_min}", 6)
    print_scr(f"Total battery time: {100 / per_min}", 7)
    print_scr(f"Current battery percent: {get_batt()}", 8)
    print_scr("Press any button to continue", 9)
    
    screens["main"].getch()
   
def long_test():
    end = 7
    print_scr(f"Starting value: {get_batt()}%", 0)
    start = get_batt()
    count = 0
    while True:
        time.sleep(1)
        print_scr(str(count) + f" current percent: {get_batt()}%", 4)
        count += 1
        if get_batt() < start - end:
            break
    per_min = (start - get_batt()) / (count / 60)

    print_scr(f"Test end. Current battery time: {get_batt() / per_min} minutes left", 5)
    print_scr(f"Battery consuption per minute: {per_min}", 6)
    print_scr(f"Total battery time: {100 / per_min}", 7)
    print_scr(f"Current battery percent: {get_batt()}", 8)
    print_scr("Press any button to continue", 9)
    screens["main"].getch()        
   

def stress():
    while not done:
        screens["main"].clear()
        i = 0
        if done:
            break
        while i < width - 2:
            j = 10
            color = colors[str(random.randint(1, 7))]
            if done:
                break
            while j < height - 2:
                if done:
                    break
                while pause:
                    pass
                time.sleep(0.005)
                screens["main"].addstr(j, i, " ", color)
                screens["main"].refresh()
                while pause:
                    pass
                if done:
                    break
                j += 1
            if done:
                break
            i += 1
        if done:
            break

def max_stress():
    while not done:
        screens["main"].clear()
        i = 0
        if done:
            break
        while i < width - 2:
            j = 10
            color = colors[str(random.randint(1, 7))]
            if done:
                break
            while j < height - 2:
                if done:
                    break
                screens["main"].addstr(j, i, " ", color)
                screens["main"].refresh()
                if done:
                    break
                j += 1
            if done:
                break
            i += 1
        if done:
            break


def short_stress_test():
    global done
    done = 0
    end = 1
    start = get_batt()
    print_scr(f"Starting value: {start}%", 0)
    count = 0
    stress_thread = task.Thread(target=stress)
    stress_thread.start()
    while True:
        pause = 1
        time.sleep(0.3)
        print_scr(str(count) + f"                                ", 4)
        print_scr(str(count) + f" current percent: {get_batt()}%", 4)
        time.sleep(0.3)
        pause = 0
        time.sleep(0.4)
        
        count += 1
        if get_batt() < start - end:
            break
    done = 1
    stress_thread.join()
    screens["main"].clear()
    screens["main"].refresh()
    per_min = (start - get_batt()) / (count / 60)
    print_scr(f"Test end. Current battery time: {get_batt() / per_min} minutes left", 5)
    print_scr(f"Battery consuption per minute: {per_min}", 6)
    print_scr(f"Total battery time: {100 / per_min}", 7)
    print_scr(f"Current battery percent: {get_batt()}", 8)
    print_scr("Press any button to continue", 9)
    
    screens["main"].getch()        
   

def med_stress_test():
    global done
    done = 0
    end = 3
    start = get_batt()
    print_scr(f"Starting value: {start}%", 0)
    count = 0
    stress_thread = task.Thread(target=stress)
    stress_thread.start()
    while True:
        pause = 1
        time.sleep(0.3)
        print_scr(str(count) + f"                                ", 4)
        print_scr(str(count) + f" current percent: {get_batt()}%", 4)
        time.sleep(0.3)
        pause = 0
        time.sleep(0.4)
        
        count += 1
        if get_batt() < start - end:
            break
    done = 1
    stress_thread.join()
    screens["main"].clear()
    screens["main"].refresh()
    per_min = (start - get_batt()) / (count / 60)
    print_scr(f"Test end. Current battery time: {get_batt() / per_min} minutes left", 5)
    print_scr(f"Battery consuption per minute: {per_min}", 6)
    print_scr(f"Total battery time: {100 / per_min}", 7)
    print_scr(f"Current battery percent: {get_batt()}", 8)
    print_scr("Press any button to continue", 9)
    screens["main"].getch()        
   
def long_stress_test():
    global done
    done = 0
    end = 7
    start = get_batt()
    print_scr(f"Starting value: {start}%", 0)
    count = 0
    stress_thread = task.Thread(target=stress)
    stress_thread.start()
    while True:
        pause = 1
        time.sleep(0.3)
        print_scr(str(count) + f"                                ", 4)
        print_scr(str(count) + f" current percent: {get_batt()}%", 4)
        time.sleep(0.3)
        pause = 0
        time.sleep(0.4)
        
        count += 1
        if get_batt() < start - end:
            break
    done = 1
    stress_thread.join()
    screens["main"].clear()
    screens["main"].refresh()
    per_min = (start - get_batt()) / (count / 60)
    print_scr(f"Test end. Current battery time: {get_batt() / per_min} minutes left", 5)
    print_scr(f"Battery consuption per minute: {per_min}", 6)
    print_scr(f"Total battery time: {100 / per_min}", 7)
    print_scr(f"Current battery percent: {get_batt()}", 8)
    print_scr("Press any button to continue", 9)
    screens["main"].getch()


def mega_stress_test():
    global done
    print_scr("This test includes fast flashing colors and will not display anything else until it is over. press 'n' to return.", 1)
    print_scr("Even if you arent sensitive to light and color changes this can be VERY DISORIENTING speaking from experience", 2)
    print_scr("After its reccomended to tilt the screen down.", 3)
    print_scr("***Press 'n' TO RETURN***", 5)
    
    key = screens["main"].getch()
    if key == ord("n"):
        return
    done = 0
    end = 1
    start = get_batt()
    print_scr(f"Starting value: {start}%", 0)
    count = 0
    stress_thread1 = task.Thread(target=max_stress)
    stress_thread1.start()
    stress_thread2 = task.Thread(target=max_stress)
    stress_thread2.start()
    stress_thread3 = task.Thread(target=max_stress)
    stress_thread3.start()
    stress_thread4 = task.Thread(target=max_stress)
    stress_thread4.start()
    stress_thread5 = task.Thread(target=max_stress)
    stress_thread5.start()
    stress_thread6 = task.Thread(target=max_stress)
    stress_thread6.start()
    while True:
        time.sleep(1)
        count += 1
        if get_batt() < start - end:
            break
    done = 1
    stress_thread1.join()
    stress_thread2.join()
    stress_thread3.join()
    stress_thread4.join()
    stress_thread5.join()
    stress_thread6.join()
    time.sleep(1)
    screens["main"].clear()
    screens["main"].refresh()
    per_min = (start - get_batt()) / (count / 60)
    print_scr(f"Test end. Current battery time: {get_batt() / per_min} minutes left", 5)
    print_scr(f"Battery consuption per minute: {per_min}", 6)
    print_scr(f"Total battery time: {100 / per_min}", 7)
    print_scr(f"Current battery percent: {get_batt()}", 8)
    print_scr("Press any button to continue", 9)
    screens["main"].getch()
    
def inps():
    cmd = {"Short Battery Test": short_test, "Medium Battery Test": med_test, "Long Battery Test": long_test, "Short Stress Test": short_stress_test, "Medium Stress Test": med_stress_test, "Long Stress Test": long_stress_test, "Max Stress": mega_stress_test}
    menu = ["Short Battery Test", "Medium Battery Test", "Long Battery Test", "Short Stress Test", "Medium Stress Test", "Long Stress Test", "Max Stress"]
    while True:
        pos = 0
        print_list(menu)
        while True:
            inp = screens["main"].getch()
            if inp == ord("e"):
                screens["main"].clear()
                screens["main"].refresh()
                cmd[menu[pos]]()
                screens["main"].clear()
                screens["main"].refresh()
                break
            elif inp == ord("w") or inp == ord("s"):
                pos = select(menu, inp, pos)

def print_list(menu):
    i = 0
    for item in menu:
        time.sleep(0.01)
        screens["main"].addstr(i, 0, item)
        screens["main"].refresh()
        i += 1

def select(menu, key, pos):
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
    screens["main"].addstr(pos - back, 0, menu[pos - back])
    screens["main"].addstr(pos, 0, menu[pos], colors["highlight"])
    return pos
wrapper(main)
