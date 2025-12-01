import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import sys
import requests
import re
import textwrap
import html
from html import unescape

height = 0
width = 0
colors = {}
screens = {}
pos = 0
ylimit = 6
globalpos = 0
recentpage = ""
link = ""
favorites = []
curusr = os.path.expanduser("~")

conf_path = curusr+"/.zinapp/browser"

if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "browser" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(conf_path)
if "favorites.conf" in os.listdir(conf_path):
    with open(conf_path+"/favorites.conf", "r") as file:
        for item in file.readlines():
            if item == " " or item == "" or item == "\n" or not item:
                continue
            favorites.append(item.strip().strip('\n'))

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
    link_win = curses.newwin(height - 5, (width // 3) - 1, 2, (width // 3) * 2)
    user_input = curses.newwin(1, width - 1, height - 1, 1)
    tbox = Textbox(user_input)
    screens.update({"top": top_bar})
    screens.update({"main": main_win})
    screens.update({"link": link_win})
    screens.update({"box": user_input})
    screens.update({"text": tbox})
    screens.update({"source": stdscr})
    colors.update({"highlight": highlight})
    colors.update({"search": curpage})
    inps(screens, colors)

def ref(screen):
    screen.clear()
    screen.refresh()

def inps(screens, colors):
    next_site = None
    prev_site = None
    fail_count = 0
    while True:
        links, page, link = homepage(next_site)
        if not page:
            fail_count += 1
            if prev_site:
                next_site = prev_site
            if fail_count >= 2:
                prev_site = None
                next_site = None
            continue
        fail_count = 0
        next_site = None
        pos = 0
        print_list(screens["main"], page, 0, 0)
        while True:    
            key = screens["main"].getch()
            if key == ord("s") or key == ord("w"):
                pos = select(screens["main"], page, key, pos)
            elif key == ord('\x1b'):
                break
            elif key == ord("S"):
                if link in favorites:
                    screens["top"].addstr(0, (width // 2) - len("already exists") // 2, "already exists", colors["highlight"])
                    screens["top"].refresh()
                    time.sleep(0.3)
                    screens["top"].addstr(0, (width // 2) - len("already exists") // 2, "              ")
                    screens["top"].refresh()
                    continue
                with open(conf_path+"/favorites.conf", "a") as file:
                    file.write(link+'\n')
                favorites.append(link)
                screens["top"].addstr(0, (width // 2) - len("saved") // 2, "saved", colors["highlight"])
                screens["top"].refresh()
                time.sleep(0.3)
                screens["top"].addstr(0, (width // 2) - len("saved") // 2, "     ")
                screens["top"].refresh()
            elif key == ord("e"):
                if not links:
                    continue
                ref(screens["link"])
                next_site = simple_input(screens["link"], links)
                if not next_site:
                    print_list(screens["main"], page, 0, 0)
                    continue
                if "http" not in next_site:
                    if link[len(link)- 1] != "/":
                        link += "/"
                    next_site = link+next_site
                prev_site = link
                log(next_site)
                break
            elif key == ord("q"):
                next_site = None
                prev_site = None
                break

def log(data):
    with open("log", "w") as file:
        file.write(str(data))

def simple_input(screen, menu):
    pos = 0
    print_list(screen, menu, 0, 0)
    screen.refresh()
    while True:
        if not pos:
            pos = 0
        key = screen.getch()
        if key == ord("s") or key == ord("w"):
            pos = select(screen, menu, key, pos)
        elif key == ord("e"):
            return menu[pos]
        elif key == ord("q"):
            return

def homepage(prefill_link=""):
    global recentpage, failed
    top = screens["top"]
    main = screens["main"]
    tbox = screens["text"]
    box = screens["box"]
    while True:
        top.clear()
        main.clear()
        homemsg = "Type URL and press Enter — Shift+s (S) to save, q to quit to home, ESC to exit"
        top.addstr(0, 0, "HomePage", colors.get("search", 0))
        main.addstr(height // 3, max(0, width // 2 - (len(homemsg) // 2)), homemsg, colors.get("highlight", 0))
        top.refresh()
        main.refresh()
        if prefill_link:
            inp = prefill_link
        else:
            while True:
                box.clear()
                box.refresh()
                curses.curs_set(1)
                tbox.win = box
                inp = tbox.edit().strip()
                curses.curs_set(0)
                if favorites and not inp:
                    ref(screens["link"])
                    inp = simple_input(screens["link"], favorites) 
                if not inp:
                    ref(main)
                    main.addstr(height // 3, max(0, width // 2 - (len(homemsg) // 2)), homemsg, colors.get("highlight", 0))
                    main.refresh()
                    continue
                break
                
        if not inp.startswith("http://") and not inp.startswith("https://"):
            inp = inp.strip(":/")
            inp = f"http://{inp}"
        top.clear()
        try:
           if len(inp) <= width - 1:
                top.addstr(0, 0, inp, colors.get("search", 0))
        except curses.error:
            pass
        top.refresh()
        try:
            resp = requests.get(inp, timeout=6)
            resp.raise_for_status()
            recentpage = inp
        except requests.exceptions.RequestException as e:
            msg = f"Could not fetch: {e}"
            main.clear()
            try:
                main.addstr(height // 3, max(0, width // 2 - (len(msg) // 2)), msg, colors.get("highlight", 0))
                main.addstr(height // 2, max(0, width // 2 - 10), "Press any key to continue", colors.get("highlight", 0))
            except curses.error:
                pass
            main.refresh()
            main.getch()
            return None, None, None
        links = extract_links(resp.text)
        lines = html_to_lines(resp.text, width - 1)
        return links, lines, inp

def html_to_lines(raw_html, wrap_width):
     raw_html = re.sub(r'(?i)</?(p|br|li|div|h[1-6]|tr|td|th|blockquote|section|article)>', '\n', raw_html)
     raw_html = re.sub(r"(?is)<style.*?>.*?</style>", "", raw_html)
     raw_html = re.sub(r"(?is)<script.*?>.*?</script>", "", raw_html)
     no_tags = re.sub(r"<[^>]+>", "", raw_html)
     text = html.unescape(no_tags)
     text = re.sub(r'\r', '', text)
     text = re.sub(r'\n[ \t]*\n+', '\n\n', text)
     text = re.sub(r'[ \t]+', ' ', text)
     parts = [p.strip() for p in text.split('\n') if p.strip()]

     lines = []
     for p in parts:
         wrapped = textwrap.wrap(p, width=wrap_width) or ['']
         lines.extend(wrapped)
     return lines

def html_to_lines(raw_html, wrap_width):
    raw_html = re.sub(r'(?i)</?(p|br|li|div|h[1-6]|tr|td|th|blockquote|section|article)>', '\n', raw_html)
    raw_html = re.sub(r"(?is)<style.*?>.*?</style>", "", raw_html)
    raw_html = re.sub(r"(?is)<script.*?>.*?</script>", "", raw_html)
    no_tags = re.sub(r"<[^>]+>", "", raw_html)
    text = html.unescape(no_tags)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n[ \t]*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    parts = [p.strip() for p in text.split('\n') if p.strip()]

    lines = []
    for p in parts:
        wrapped = textwrap.wrap(p, width=wrap_width) or ['']
        lines.extend(wrapped)
    return lines

def extract_links(html):
    html = unescape(html)
    link_pattern = re.compile(
        r'<a[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL
    )

    links = []
    for match in link_pattern.finditer(html):
        url = match.group(1).strip()
        links.append(url)
    return links

def select(screen, page, key, pos):
    global globalpos
    if key == ord("s"):
        pos += 1
        if pos + globalpos >= len(page):
            pos -= 1
        back = 1
        if pos == height - ylimit:
            globalpos += pos
            pos = 0
            back = 0
            print_list(screens, colors, page, 0, globalpos)
    elif key == ord("w"):
        pos -= 1
        if pos < 0:
            pos = 0
        back = -1
        if pos < 1 and globalpos:
            globalpos -= height - ylimit
            pos = height - ylimit - 1
            back = 0
            screen.clear()
            print_list(screens, colors, page, 0, globalpos)
    if len(page) > 1:
        screen.addstr(pos - back, 0, page[pos + globalpos - back])
    screen.addstr(pos, 0, page[pos + globalpos], colors["highlight"])
    return pos

def print_text(screen, string, y):
    to_print = []
    for char in string:
        if char == '\n':
            text, string = string.split('\n', 1)
            to_print.append(text)
    to_print.append(string)
    for item in cache_list:
        if y >= height - ylimit:
            break
        screen.addstr(y, 0, item)
        y += 1
    screen.refresh()


def print_list(screen, text_list, y, offset):
    cache_list = []
    for item in text_list:
        cache_list.append(item)
    if offset:
        screen.clear()
        while offset != 0:
            cache_list.remove(text_list[offset])
            offset -= 1
        with open("list2.txt", "w") as file:
            for item in cache_list:
                file.write(f"{item}\n")
    for item in cache_list:
        if y >= height - ylimit:
            break
        screen.addstr(y, 0, item)
        y += 1
    screen.refresh()


wrapper(main)
