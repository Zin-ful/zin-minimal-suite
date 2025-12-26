from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom

grid_size = 800

grid_width = 40


#ip = input("Enter server IP: ")
#if not ip:
#    ip = "localhost"

grid = {}

ships = {"Battleship": {"size": 7, "icon": "B"}, "Aircraft Carrier": {"size": 7, "icon": "A"},
"Heavy Cruiser": {"size": 6, "icon": "H"},"Light Cruiser": {"size": 6, "icon": "L"},"Destroyer": {"size": 5, "icon": "D"}, 
"Minelayer": {"size": 5, "icon": "M"}, "Gunboat": {"size": 4, "icon": "G"}, "Submarine": {"size": 4, "icon": "s"}, 
"Minesweeper": {"size": 3, "icon": "m"}, "Corvette": {"size": 3, "icon": "c"}}


def gen_grid():
    for i in range(grid_size):
        grid.update({i: "."})

def print_grid():
    i = 1
    j = 1
    line = ""
    top = ""
    for i in range(grid_width - 1):
        if i < 9:
            top += f"0{i + 1} "
        else:
            top += f"{i + 1} "
    print("    "+top)
    i = 1
    for pos, item in grid.items():
        line += f"{item}  "
        i += 1
        if i == grid_width:
            if j < 10:
                print(f"0{j}: {line}")
            else:
                print(f"{j}: {line}")
            line = ""
            j += 1
            i = 1


def apply_ship_to_grid(direction, coord, ship):
    side, top = coord
    size = ships[ship]["size"]
    icon = ships[ship]["icon"]
    side += 1
    top *= side
    if "v" in direction:
        if side - size < 1:
            side = size // 2
        elif side + size > grid_size // grid_width:
            side = grid_size // grid_width
            side -= size // 2
        test = top
        for i in range(size):
            if grid[test] != ".":
                print("Object already there")
                return
            test += grid_width - 1
        for i in range(size):
            grid.update({top: icon})
            top += grid_width - 1

    else:
        if top - size < 1:
            top = size // 2
        elif top + size > grid_width:
            top = grid_width - (size // 2)

        test = top
        for i in range(size):
            if grid[test] != ".":
                print("Object already there")
                return
            test += grid_width - 1
        
        for i in range(size):
            grid.update({top: icon})
            top += 1

def select_ship():
    i = 1
    ship_list = []
    for item, attr in ships.items():
        print(f"{i}. {item} - size: {attr['size']}")
        ship_list.append(item)
        i += 1
    while True:
        choice = input("Select ship: ")
        try:
            choice = int(choice.strip())
            if choice - 1 > len(ship_list) - 1 or choice < 1:
                print("Out of the range of selection, try again")
                continue
            break
        except:
            print("That isnt a option")

    ship = ship_list[choice - 1]
    dir = input("Select rotation (horizontal/vertical): ")
    while True:
        print_grid()
        pos_1 = input("Select position (side): ")
        pos_2 = input("Select position (top): ")
        try:
            pos_1 = int(pos_1.strip())
            pos_2 = int(pos_2.strip())
            break
        except:
            print("That isnt a option")
    
    apply_ship_to_grid(dir, (pos_1, pos_2), ship)

gen_grid()
while True:
    select_ship()
    print_grid()
