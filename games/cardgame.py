from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import curses
import time
from curses import wrapper
from curses.textpad import Textbox
import random

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
    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_BLACK)
    clear_color = curses.color_pair(11)
    #general
    top_window = curses.newwin(0, width, 0, 0)
    middle_window = curses.newwin(1, width, height // 3, 0)
    bottom_window = curses.newwin(1, width, (height - (height // 10) - 2), 0)
    main_window = curses.newwin(height - 5, width, 2, 0)
    input_window = curses.newwin(1, width - 1, height - 1, 1)

    opposition_field = curses.newwin(height // 2, width - 1, 0, 1)
    player_field = curses.newwin(height // 2, width - 1, height // 2, 1)
    
    card_window = curses.newwin(height - (height // 3), width // 3, height // 4, width // 3)
    card_one = curses.newwin(height // 4, width // 8, height // 2 + 5, (width // 5))
    card_two = curses.newwin(height // 4, width // 8, height // 2 + 5, (width - (width // 2)) - 10)
    card_three = curses.newwin(height // 4, width // 8, height // 2 + 5, (width - (width // 4)) - 13)

    hand_one = curses.newwin(height // 10, width // 6, height - (height // 10), width // 3)
    hand_two = curses.newwin(height // 10, width // 6, height - (height // 10), (width // 3) + width // 6)
    hand_three = curses.newwin(height // 10, width // 6, height - (height // 10), (width // 3) + width // 3)
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
    
    screens.update({"hand one": hand_one})
    screens.update({"hand two": hand_two})
    screens.update({"hand three": hand_three})
    screens.update({"middle bar": middle_window})
    screens.update({"bottom bar": bottom_window})
    screens.update({"card one": card_one})
    screens.update({"card two": card_two})
    screens.update({"card three": card_three})

    #screen dimensions
    dims.update({"middle bar": middle_window.getmaxyx()})
    dims.update({"top bar": top_window.getmaxyx()})
    dims.update({"main": main_window.getmaxyx()})
    dims.update({"input window": input_window.getmaxyx()})
    dims.update({"source": stdscr.getmaxyx()})
    dims.update({"bottom bar": bottom_window.getmaxyx()})
    
    dims.update({"non-player": opposition_field.getmaxyx()})
    dims.update({"player": player_field.getmaxyx()})
    dims.update({"card detail": card_window.getmaxyx()})
    dims.update({"card one": card_one.getmaxyx()})
    dims.update({"card two": card_two.getmaxyx()})
    dims.update({"card three": card_three.getmaxyx()})

    #dims.update({"pause": pause_window.getmaxyx()})
    dims.update({"hand one": hand_one.getmaxyx()})
    dims.update({"hand two": hand_two.getmaxyx()})
    dims.update({"hand three": hand_three.getmaxyx()})


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
    colors.update({"clear": clear_color})
    
    #process
    #test(hand_one)
    #test(hand_two)
    #test(hand_three)
    test(bottom_window)
    init()
    stdscr.clear()
    stdscr.refresh()
    game_menu()
    #inps(menu_list, menu_dict)

def draw(screen, color, y, x):
    screen.addstr(y, x, " ", color)

def test(screen):
    screens["source"].clear()
    screens["source"].refresh()
    j = 1
    while j < height - 1:
        i = 1
        while i < width - 1:
            i += 1
            draw(screens["source"], colors["blue 2"], j, i)
        j += 1
    screens["source"].refresh()
    screen.clear()
    screen.refresh()
    time.sleep(1)


def local_inps(menu):
    print_list(menu, 0, globalpos)
    while True:
        key = screens["main"].getch()
        if key == ord("s") or key == ord("w"):
            select(key, menu)
        if key == ord("e"):
            return menu[pos]


def empty_inps():
    key = screens["main"].getch()
    if key == ord("a"):
        return -1
    elif key == ord("d"):
        return 1
    elif key == ord(" "):
        return " "
    else:
        return 0
    
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

def userwait():
    key = screens["main"].getch()
    if key:
        return key

def log(data):
    with open("log.txt", "w") as file:
        file.write(str(data))
def ref(screen):
    screens[screen].clear()
    screens[screen].refresh()

"""Actual program functions"""

def game_menu():
    draw_amount = 5
    height, width = dims["player"]
    screens["main"].clear()
    screens["main"].refresh()
    hand = []
    deck = gen_deck(50)
    for i in range(draw_amount):
        name = draw_card(deck, i)
        deck.remove(name)
        hand.append(name)
        
    clr(5, width // 2)
    
    ref("card detail")
    render_deck(len(deck), height - 1, 0)
    render_hand(hand, 0, None)
    val = 1
    while True: 
        inp = empty_inps()
        if inp:
            if inp == " ":
                play_turn()
                continue
            val += inp
            if val < 1:
                val = 1
            if val > 3:
                val = 3
            render_hand(hand, val, "bottom bar")
        else:
            if len(card_space) == 3:
                continue
            if len(hand) == 1:
                for i in range(draw_amount - len(hand)):
                    name = draw_card(deck, i)
                    deck.remove(name)
                    hand.append(name)
                render_deck(len(deck), height - 1, 0)
                ref("card detail")
                screens["player"].refresh()
                render_hand(hand, 0, None)
                if card_space:
                    for name, val in card_space.items():
                        deck.remove(name)
                        render_card(all_cards[name], 2, val)
                #screens["hand one"].refresh()
                #screens["hand two"].refresh()
                #screens["hand three"].refresh()
                continue
            table_pos = 1
            while True:
                inp = empty_inps()
                if inp:
                    table_pos += inp
                    if table_pos < 1:
                        table_pos = 1
                    if table_pos > 3:
                        table_pos = 3
                    render_hand(hand, table_pos, "middle bar")
                else:
                    ref("middle bar")
                    hand.remove(hand[val - 2])
                    render_hand(hand, 0, None)
                    render_card(all_cards[hand[val - 2]], 2, table_pos)
                    card_space.update({hand[val - 2]:table_pos})
                    log(all_cards[hand[val - 2]])
                    break

def play_turn(enemy):
    if not len(card_space):
        return
    for name, val in card_space.items()
        attack = all_cards[name]["Attack"]
        enemy["Health"] -= attack
        

def clr(y, x):
    screens["main"].addstr(y,x, " ", colors["clear"])
    screens["main"].refresh()

def draw_card(deck, number):
    choice = random.randint(0, len(deck) - 1)
    render_card(all_cards[deck[choice]], 1, 0)
    screens["main"].addstr(5, width // 2, str(number + 1), colors["red 1"])
    screens["main"].refresh()
    userwait()
    return deck[choice]

def gen_deck(num):
    deck = []
    for _ in range(num):
        randnum = random.randint(0, len(player_data["Cards"]) - 1)
        deck.append(player_data["Cards"][randnum])
    return deck
    

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
    #screens["main"].clear()
    cards = player_data["Cards"]
    i = 0
    while True:
        render_card(all_cards[cards[i]], 1, 0)
        value = empty_inps()
        if value == 0:
            break
        else:
            i += value
        if i < 0:
            i = 0
        elif i > len(cards) - 1:
            i = len(cards) - 1

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

def render_deck(number, y, x):
    if number < 2:
        color = colors["red 2"]
    else:
        color = colors["white"]
    screens["player"].addstr(y - 1, x + 5, str(number), color)

    draw(screens["player"], colors["white"], y - 1, x)
    draw(screens["player"], colors["white"], y - 1, x + 1)
    draw(screens["player"], colors["white"], y - 1, x + 2)
    draw(screens["player"], colors["white"], y - 1, x + 3)

    draw(screens["player"], colors["white"], y - 2, x)
    draw(screens["player"], colors["white"], y - 2, x + 1)
    draw(screens["player"], colors["white"], y - 2, x + 2)
    draw(screens["player"], colors["white"], y - 2, x + 3)

    draw(screens["player"], colors["white"], y - 3, x)
    draw(screens["player"], colors["white"], y - 3, x + 1)
    draw(screens["player"], colors["white"], y - 3, x + 2)
    draw(screens["player"], colors["white"], y - 3, x + 3)
 
    screens["player"].refresh()

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
        screens[card_name].addstr(height - 4, 1, f"Attack: {card['Attack']}", colors[detail["text"]])
        screens[card_name].addstr(height - 3, 1, f"Magic: {card['Magic']}", colors[detail["text"]])
        screens[card_name].addstr(height - 2, 1, f"Defense: {card['Defense']}", colors[detail["text"]])

        screens[card_name].refresh()
    if size == 3:
        if number == 1:
            card_name = "hand one"
        elif number == 2:
            card_name = "hand two"
        elif number == 3:
            card_name = "hand three"
        dim = dims.get(card_name)
        height = dim[0]
        width = dim[1]
        fill_screen(card_name, detail["border"], 0)
        fill_screen(card_name, detail["color"], 1)
        screens[card_name].addstr(0, 1, detail["name"], colors[detail["text"]])
        screens[card_name].addstr(1, 1, f"Cst:{card['Cost']}", colors[detail["text"]])
        screens[card_name].refresh()

def render_hand(deck, selected, bar):
    i = 1
    if not selected:
        ref("hand one")
        ref("hand two")
        ref("hand three")
        for item in deck:
            render_card(all_cards[item], 3, i)
            i += 1
            if i == 4:
                break
    else:
        render_select(bar, selected)



def render_select(bar, sel):
    height, width = dims[bar]
    screens[bar].clear()
    if sel == 1:
        screens[bar].addstr(0, width // 3 + (width // 12), "  ", colors["white"])
    elif sel == 2:
        screens[bar].addstr(0, (width // 3) + width // 6 + (width // 12), "  ", colors["white"])
    elif sel == 3:
        screens[bar].addstr(0, (width // 3) + width // 3 + (width // 12), "  ", colors["white"])
    screens[bar].refresh()

"""Startup"""

def load():
    if "user_stats.conf" not in os.listdir(conf_path):
        return 0
    with open(conf_path+"user_stats.conf", "r") as file:
        data = file.readlines()
        for item in data:
            name, value = item.split(":")
            if "[" not in value:
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
    for name, val in all_cards.items():
        card_names.append(name)
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
    player_data.update({"Cards": ["Knight", "Mage", "Priest"]})
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
"design": {"name":"Familiar","border": "white", "shape": "box", "color": "green 2", "text": "green 1", "description": "Unknown through sight"}},
}
card_names = []


#init()
wrapper(main)
