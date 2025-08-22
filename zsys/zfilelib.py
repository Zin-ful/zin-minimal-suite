import os
import time
import curses
data_name = ""
data_path = ""

pos = 0
sx = 0
lvl = 0
origin = 0
num = 0

ylimit = 4

cur_dir = "/home"
files_in_path = os.listdir(cur_dir)
SELECT = None
data = None
hidden = 1

def list_file(win, delay, rst):
    global origin, files_in_path, pos, sx, lvl, num
    time.sleep(0.1)
    win.clear()
    files_in_path = os.listdir(cur_dir)
    if rst:
        pos = 0
        lvl = 0
        num = 0
    sx = 0
    i = 0
    y = 0
    x = 0
    for item in files_in_path.copy():
        if item[0] == "." and hidden:
            files_in_path.remove(item)
    for item in files_in_path:
        if num * (height - ylimit) + i >= len(files_in_path):
            break
        if x >= width - 5:
            return
        else:
            win.addstr(y, x, files_in_path[num * (height - ylimit) + i], curses.COLOR_WHITE)
        i += 1
        y += 1
        if y >= height - ylimit:
            x += width // 3
            y = 0
        time.sleep(delay)
        win.refresh()

def get_file(win):
    global cur_dir, pos, origin
    win.clear()
    win.refresh()
    list_file(0.001, 1)
    while True:
        key = win.getch()
        if key == -1:
            continue
        if key == ord("a") or key == ord("d"):
            cur_dir = move(key)
            list_file(0.002, 1)
            win.refresh()
        elif key == ord("w") or key == ord("s"):
            select_file(key, "files", files_in_path, None)
        elif key == ord("e"):
            return cur_dir+"/"+files_in_path[pos]
        elif key == ord('q'):
            return

def select_file(win, inp, word_list, xoffset):
    global pos, sx, lvl, num
    if not xoffset:
        xoffset = 0
    if not word_list or len(word_list) < 0:
        win.addstr(1, 0, "NO FILES IN PATH", curses.COLOR_RED)
        win.refresh()
        return
    if inp == ord("s"):
        pos += 1
        offset = 1
    elif inp == ord("w"):
        offset = -1
        pos -= 1
    prevlen = ""
    if pos >= height - ylimit and len(word_list) > height - ylimit and subwin == "files":
        pos = 0
        lvl += 1
        sx += width // 3
        if sx >= width - 3:
            if sx // width == 0:
                num += 3
            else:
                num += 3
            list_file(win, 0.002, 0)
    elif pos == -1 and lvl >= 1 and subwin == "files":
        sx -= width // 3
        pos = height - ylimit - 1
        lvl -= 1
        if sx < 0 and num:
            num -= 3
            list_file(0.002, 0)
            sx = (width - width // 3)

    if pos <= 0:
        offset = 0
        pos = 0
    elif pos >= len(word_list):
        pos = len(word_list) - 1
        offset = 0
    for i in word_list[pos]:
        prevlen += " "
    if lvl:
        lvl_offset = (height - ylimit) * lvl
    else:
        lvl_offset = 0
    if pos + lvl_offset >= len(files_in_path) and subwin == "files":
        pos -= 1
    final_pos = origin + pos - offset
    if subwin == "files":
        if pos > -1:
            if  final_pos >= height - ylimit or final_pos >= len(files_in_path):
                pass
            else:
                win.addstr(final_pos, sx + xoffset, prevlen, curses.COLOR_BLACK)
                win.addstr(final_pos, sx + xoffset, word_list[pos - offset + lvl_offset], curses.COLOR_BLACK)
        win.addstr(origin + pos, sx + xoffset, word_list[pos + lvl_offset])
    else:
        if pos > -1:
            win.addstr(final_pos, sx + xoffset, prevlen, curses.COLOR_BLACK)
            win.addstr(final_pos, sx + xoffset, word_list[pos - offset], curses.COLOR_BLACK)
        win.addstr(origin + pos, sx + xoffset, word_list[pos])
    win.refresh()

def move(inp):
    rev_dir = os.path.dirname(f"{cur_dir}..")
    if files_in_path or len(files_in_path) > 0:
        if cur_dir == "/":
            forw_dir = cur_dir + files_in_path[num * sx + pos]
        else:
            if not num and sx:
                calc = (lvl * (height - ylimit)) + pos
                forw_dir = cur_dir + "/" + files_in_path[calc]
            else:
                calc = (lvl * (height - ylimit)) + pos
                forw_dir = cur_dir + "/" + files_in_path[calc]
    if inp == ord("a"):
        if cur_dir == "/":
            return "/"
        else:
            try:
                var = os.listdir(rev_dir)
            except:
                return cur_dir
            return rev_dir
    elif inp == ord("d"):
        try:
            var = os.listdir(forw_dir)
        except:
            return cur_dir
        return forw_dir

