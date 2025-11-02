from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import curses
import time
from curses import wrapper
from curses.textpad import Textbox

curusr = os.path.expanduser("~")

#setup
height = 0
width = 0
dims = {}
colors = {}
screens = {}
pos = 0
ylimit = 6
globalpos = 0
conf_path = curusr+"/.zinapp/cardgame/"
#network
server = netcom.socket(ipv4, tcp)
ip = "localhost"
port = 10592
online = 1
#game
card_space = {}
full_deck = {}
player_deck = {}
player_data = {}

#utils
menu_list = ["Play","Shop","Stats","Online","Deck","Settings"]

def main(stdscr):
    global height, width

    height, width = stdscr.getmaxyx()
    
    #text color options
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    green_1 = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
    green_2 = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    red_1 = curses.color_pair(3)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)
    red_2 = curses.color_pair(4)    
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
    black_1 = curses.color_pair(5)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    blue_1 = curses.color_pair(6)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLUE)
    blue_2 = curses.color_pair(7)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
    white_1 = curses.color_pair(8)
    curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    yellow_1 = curses.color_pair(9)
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    yellow_2 = curses.color_pair(10)
    
    #general
    top_window = curses.newwin(0, width, 0, 0)
    bottom_window = None
    main_window = curses.newwin(height - 5, width, 2, 0)
    input_window = curses.newwin(1, width - 1, height - 1, 1)

    opposition_field = curses.newwin(height // 2, width - 1, 0, 1)
    player_field = curses.newwin(height // 2, width - 1, height // 2, 1)
    
    card_window = curses.newwin(height - (height // 3), width // 3, height // 4, width // 3)
    card_one = curses.newwin(height // 4, width // 8, height // 2 + 5, (width // 5))
    card_two = curses.newwin(height // 4, width // 8, height // 2 + 5, (width - (width // 2)) - 10)
    card_three = curses.newwin(height // 4, width // 8, height // 2 + 5, (width - (width // 4)) - 13)
    deck_window = None
    pause_window = None
    user_input = Textbox(input_window)

    #player field
    screens.update({"top bar": top_window})
    screens.update({"main": main_window})
    screens.update({"input window": input_window})
    screens.update({"user input": user_input})
    screens.update({"source": stdscr})

    screens.update({"non-player": opposition_field})
    screens.update({"player": player_field})
    screens.update({"card detail": card_window})
    screens.update({"pause": pause_window})
    screens.update({"bottom bar": bottom_window})
    screens.update({"card one": card_one})
    screens.update({"card two": card_two})
    screens.update({"card three": card_three})

    #screen dimensions
    
    dims.update({"top bar": top_window.getmaxyx()})
    dims.update({"main": main_window.getmaxyx()})
    dims.update({"input window": input_window.getmaxyx()})
    dims.update({"source": stdscr.getmaxyx()})

    dims.update({"non-player": opposition_field.getmaxyx()})
    dims.update({"player": player_field.getmaxyx()})
    dims.update({"card detail": card_window.getmaxyx()})
    dims.update({"card one": card_one.getmaxyx()})
    dims.update({"card two": card_two.getmaxyx()})
    dims.update({"card three": card_three.getmaxyx()})
    #dims.update({"pause": pause_window.getmaxyx()})
    #dims.update({"bottom bar": bottom_window.getmaxyx()})


    #colors
    colors.update({"green 1": green_1})
    colors.update({"green 2": green_1})
    colors.update({"red 1": red_1})
    colors.update({"red 2": red_2})
    colors.update({"black": black_1})
    colors.update({"blue 1": blue_1})
    colors.update({"blue 2": blue_2})
    colors.update({"white": white_1})
    colors.update({"yellow 1": yellow_1})
    colors.update({"yellow 2": yellow_2})
    
    #process
    render_card(all_cards["Knight"], 2, 1)
    render_card(all_cards["Mage"], 2, 2)
    render_card(all_cards["Familiar"], 2, 3)
    
    #test(stdscr, card_one, blue_2)
    #test(stdscr, card_two, blue_2)
    #test(stdscr, card_three, blue_2)
    #init()
    #stdscr.clear()
    #stdscr.refresh()
    #inps(menu_list, menu_dict)

def draw(screen, color, y, x):
    screen.addstr(y, x, " ", color)

def test(screen, screen_2, pair):
    screen.clear()
    screen.refresh()
    j = 1
    while j < height - 1:
        i = 1
        while i < width - 1:
            i += 1
            draw(screen, pair, j, i)
        j += 1
    screen.refresh()
    screen_2.clear()
    screen_2.refresh()
    time.sleep(1)


def local_inps(menu):
    print_list(menu, 0, globalpos)
    while True:
        key = screens["main"].getch()
        if key == ord("s") or key == ord("w"):
            select(key, menu)
        if key == ord("e"):
            return menu[pos]

    
def inps(menu, dict):
    global pos
    print_list(menu, 0, globalpos)
    while True:
        key = screens["main"].getch()
        if key == ord("s") or key == ord("w"):
            select(key, menu)
        if key == ord("e"):
            cmd = dict.get(menu[pos])
            if cmd:
                cmd()
                screens["main"].clear()
                print_list(menu, 0, globalpos)
                pos = 0
def select(key, menu):
    global pos, globalpos
    if key == ord("s"):
        pos += 1
        if pos + globalpos >= len(menu):
            pos -= 1
        back = 1
        if pos == height - ylimit:
            globalpos += pos
            pos = 0
            back = 0
            print_list(menu, 0, globalpos)
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
        if pos < 1 and globalpos:
            globalpos -= height - ylimit
            pos = height - ylimit - 1
            back = 0
            screens["main"].clear()
            print_list(menu, 0, globalpos)
    screens["main"].addstr(pos - back, 0, menu[pos + globalpos - back])
    screens["main"].addstr(pos, 0, menu[pos + globalpos], colors["white"])

def print_text(string, y):
    to_print = []
    for char in string:
        if char == '\n':
            text, string = string.split('\n', 1)
            to_print.append(text)
    to_print.append(string)
    for item in cache_list:
        if y >= height - ylimit:
            break
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()


def print_list(text_list, y, offset):
    cache_list = []
    for item in text_list:
        cache_list.append(item)
    if offset:
        screens["main"].clear()
        while offset != 0:
            cache_list.remove(text_list[offset])
            offset -= 1
    for item in cache_list:
        if y >= height - ylimit:
            break
        screens["main"].addstr(y, 0, item)
        y += 1
    screens["main"].refresh()

def userwait(screens):
    key = screens["main"].getch()
    if key:
        return key

"""Actual program functions"""

def game_menu():
    return

def shop_menu():
    return

def stat_menu():
    screens["main"].clear()
    data_list = []
    for name, value in player_data.items():
        data_list.append(name)
    stat = local_inps(data_list)
    
def start_online():
    return

def view_cards():
    return

def settings():
    return 

def fill_screen(screen, color, offset):
    dim = dims.get(screen)
    height = dim[0]
    width = dim[1]
    j = 0
    if offset:
        j += offset
    while j < (height - 1) - offset:
        i = 0
        if offset:
            i += offset
        while i < (width - 1) - offset:
            i += 1
            draw(screens[screen], colors[color], j, i)
        j += 1
    screens[screen].refresh()
       

def intro(screens, colors):
    return


def render_card(card, size, number): #size 1-3 
    detail = card["design"]
    if size == 1: #"name":"border": "white" "color": "white" "text": "black"       
        dim = dims.get("card detail")
        height = dim[0]
        width = dim[1]
        fill_screen("card detail", detail["border"], 0)
        fill_screen("card detail", detail["color"], 1)

        screens["card detail"].addstr(0, 1, detail["name"], colors[detail["text"]])
        screens["card detail"].addstr(0, (width // 2) - 3, f"Cost: {card['Cost']}", colors[detail["text"]])
        screens["card detail"].addstr(0, width - (width // 3) + 3, f"Act: {card['Action']}", colors[detail["text"]])
        
        screens["card detail"].addstr(height - 10, 1, detail["description"], colors[detail["text"]])
        screens["card detail"].addstr(height - 7, 1, f"Attack: {card['Attack']}", colors[detail["text"]])
        screens["card detail"].addstr(height - 6, 1, f"Magic: {card['Magic']}", colors[detail["text"]])
        screens["card detail"].addstr(height - 5, 1, f"Defense: {card['Defense']}", colors[detail["text"]])

        screens["card detail"].refresh()

    if size == 2: #"name":"border": "white" "color": "white" "text": "black"
        if number == 1:
            card_name = "card one"
        elif number == 2:
            card_name = "card two"
        elif number == 3:
            card_name = "card three"
        dim = dims.get(card_name)
        height = dim[0]
        width = dim[1]
        fill_screen(card_name, detail["border"], 0)
        fill_screen(card_name, detail["color"], 1)
        
        screens[card_name].addstr(0, 1, detail["name"], colors[detail["text"]])
        screens[card_name].addstr(1, 1, f"Cst:{card['Cost']}", colors[detail["text"]])
        screens[card_name].addstr(2, 1, f"Act:{card['Action']}", colors[detail["text"]])
        screens[card_name].addstr(height - 7, 1, f"Attack: {card['Attack']}", colors[detail["text"]])
        screens[card_name].addstr(height - 6, 1, f"Magic: {card['Magic']}", colors[detail["text"]])
        screens[card_name].addstr(height - 5, 1, f"Defense: {card['Defense']}", colors[detail["text"]])

        screens[card_name].refresh()





"""Startup"""

def load():
    if "user_stats.conf" not in os.listdir(conf_path):
        return 0
    with open(conf_path+"user_stats.conf", "r") as file:
        data = file.readlines()
        for item in data:
            name, value = item.split(":")
            value = int(value)
            player_data.update({name: value})

def save():    
    with open(conf_path+"user_stats.conf", "w") as file:
        for name, value in player_data.items():
            file.write(f"{name}:{value}\n")


def init():
    global online
    #print("running through init")
    #print("current user: ", curusr)
    #time.sleep(0.5)
    if ".zinapp" not in os.listdir(curusr):
        os.mkdir(curusr+"/.zinapp")
        #print("making conf dir")
    else:
        print("dir .zinapps exists")
    #time.sleep(0.5)
    if "cardgame" not in os.listdir(curusr+"/.zinapp"):
        os.mkdir(conf_path)
        #print("making conf dir")
    else:
        print("dir cardgame exists")
    #time.sleep(0.5)
    try:
        #print("attempting connection to online servers")
        server.connect((ip, int(port)))        
    except:
        #print("server connection failed, offline only")
        online = 0
    #time.sleep(0.5)
    if online:
        ack = server.recv(3).decode("utf-8")
        if ack == "ack":
            server.send("ack".encode("utf-8"))
    #print("checking screens")
    #time.sleep(0.5)
    for name, val in screens.items():
        print(name)
    #time.sleep(0.5)
    #print("checking colors")
    #time.sleep(0.5)
    for name, val in colors.items():
        print(name)
    #time.sleep(0.5)
    #print("checking dimensions")
    #time.sleep(0.5)
    #print("screen size: ", height, width)
    for name, val in dims.items():
        print(f"{name}: {val}")
    if not load():
        create_player()
    #print("init finished")
    #time.sleep(2)

def create_player():
    player_data.update({"Health": 100})
    player_data.update({"Strength": 10})
    player_data.update({"Defense": 0})
    player_data.update({"Energy": 100})
    player_data.update({"Exp": 0})
    player_data.update({"Sp": 0})    
    player_data.update({"Level": 0})

    with open(conf_path+"user_stats.conf", "w") as file:
        for name, value in player_data.items():
            file.write(f"{name}:{value}\n")
menu_dict = {"Play": game_menu, "Shop": shop_menu, "Stats": stat_menu, "Online": start_online, "Deck": view_cards, "Settings": settings}

all_cards = {
"Knight":{"type":"Physical", "Health": 30, "Attack": 7, "Defense": 5, "Magic": 0, "Cost": 10, "Action": 5, 
"design": {"name":"Knight","border": "white", "shape": "box", "color": "white", "text": "black", "description": "Sworn through oath"}},
"Mage":{"type":"Magic", "Health": 15, "Attack": 10, "Defense": 0, "Magic": 20, "Cost": 25 , "Action": 15, 
"design": {"name":"Mage","border": "blue 2", "shape": "box", "color": "white", "text": "black", "description": "Bound by knowledge"}},
"Priest":{"type":"Support", "Health": 20, "Attack": 0, "Defense": 5, "Magic": 30, "Cost": 35, "Action": 0, 
"design": {"name":"Priest","border": "white", "shape": "box", "color": "yellow 2", "text": "black", "description": "Free through faith"}},
"Familiar":{"type":"Spirit", "Health": 50, "Attack": 5, "Defense": 0, "Magic": 10, "Cost": 20, "Action": 10, 
"design": {"name":"Familiar","border": "white", "shape": "box", "color": "green 2", "text": "black", "description": "Unknown through sight"}},
}



#init()
wrapper(main)
