from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import time
import random
import threading
import base64

conf_path = "/etc/oneturnserver"

words = ["one","into","a","seat","flip","not","unset","nail","joke","laugh","enjoy","old","eye","file","bring","love","lie","sprawl","shook","rather","involved","time","right","there","left","tell","camera","before","more","over","flee","stand","rush","friend","address","of","emergecy","guy","got","down","couple", "hunt", "run","without","help","trace","old","year","state","car", "hands", "arrived", "anyone", "on", "this", "fall","high","try","burn","toss","lap","cant","did","do","too","to","two","flow","tan","brain","glove","county","had","come","here","room","work"]


p1name = ""
p1health = 20
p1points = 0
p1level = 0
p1exp = 0
p1expreq = 0
p1attack= 0
p1defense = 0
p1speed = 0


p2name = ""
p2health = 20
p2points = 0
p2level = 0
p2exp = 0
p2expreq = 0
p2attack = 0
p2defense = 0
p2speed = 0

p1stats = {"name": p1name, "hp": p1health, "pnt": p1points, "lvl": p1level, "xp": p1exp, "req": p1expreq, "atk": p1attack, "def": p1defense, "spd": p1speed}

p2stats = {"name": p2name,"hp": p2health, "pnt": p2points, "lvl": p2level, "xp": p2exp, "req": p2expreq, "atk": p2attack, "def": p2defense, "spd": p2speed}

port = int(input("port: "))

p1ready = 0
p2ready = 0

server = netcom.socket(ipv4, tcp)
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", port))

if "oneturnserver" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)

server.listen(2)




def player1start(server):
	global p1alive, p1stats
	try:
		while True:
			player1, player1ip = server.accept()
			ack = player1.recv(1024).decode("utf-8")
			if ack:
				player1.send("ack".encode("utf-8"))
				p1alive = True
				cmd = player1.recv(1024).decode("utf-8")
				if cmd:
					if "login" in cmd:
						player1.send("username please.".encode("utf-8"))
						login_info = player1.recv(1024).decode("utf-8")
						if login_info:
							login(login_info, 1)
							p1shell(player1)
					else:
						player1.send("you need to login first".encode("utf-8"))
	except Exception as e:
		print(e)
		player1.shutdown(netcom.SHUT_RDRW)
		player1.close()
	

def player2start(server):
	global p2alive, p2stats
	try:
		while True:
			player2, player2ip = server.accept()
			ack = player2.recv(1024).decode("utf-8")
			if ack:
				player2.send("ack".encode("utf-8"))
				p2alive = True
				cmd = player2.recv(1024).decode("utf-8")
				if cmd:
					if "login" in cmd:
						player2.send("username please.".encode("utf-8"))
						login_info = player2.recv(1024).decode("utf-8")
						if login_info:
							login(login_info, 2)
							p2shell(player2)
					else:
						player2.send("you need to login first".encode("utf-8"))
	except Exception as e:
		print(e)
		player2.shutdown(netcom.SHUT_RDRW)
		player2.close()
						
def p1shell(player1):
	player1.send("Welcome, player 1".encode("utf-8"))
	while True:
		cmd = player1.recv(128).decode("utf-8")
		if "fight" in cmd:
			p1fight(player1)
		elif "stats" in cmd:
			for name, val in p1stats.items():
				to_send += f"{name} = {val}\n" 
			player1.send(to_send.encode("utf-8"))

def p2shell(player2):
	player2.send("Welcome, player 2".encode("utf-8"))
	while True:
		cmd = player2.recv(128).decode("utf-8")
		if "fight" in cmd:
			p2fight(player2)
		elif "stats" in cmd:
			for name, val in p2stats.items():
				to_send += f"{name} = {val}\n" 
			player2.send(to_send.encode("utf-8"))

def login(info, player):
	pfile = f"{conf_path}/{info}.conf"
	if pfile in os.listdir(conf_path):
		with open(pfile, "r") as file:
			pdata = file.readlines()
			for item in pdata:
				name, val = item.split("=")
				if name == "name":
					if player == 2:
						p2stats[name] = val
					else:
						p1stats[name] = val
				else:
					if player == 1:
						p2stats[name] = int(val)
					else:
						p1stats[name] = int(val)
	else:
		with open(pfile, "w") as file:
			if player == 2:
				p2stats["name"] = info
				for name, val in p2stats.items():
					file.write(f"{name}={val}\n")
			if player == 1:
				p1stats["name"] = info
				for name, val in p1stats.items():
					file.write(f"{name}={val}\n")
		
def p1fight(player1):
	global p1ready
	cachehp = p1stats["hp"]
	player1.send("are you ready? (wating for other players confirmation)".encode("utf-8"))
	conf = player1.recv(48).decode("utf-8")
	if "y" in conf:
		p1ready = 1
	else:
		return
	while not p2ready:
		pass
	while not p1ready:
		pass
	while True:
		spellme = words[random.randint(0, len(words) - 1)]
		score = 0
		count = random.randint(0,7 + (p1stats["spd"] // 10))
		time_thread = threading.Thread(target=timer, args=(count,))
		time_thread.start()
		while not done:
			spellme = words[random.randint(0, len(words) - 1)]
			player1.send(f"Word: {spellme}".encode("utf-8"))
			inp = player1.recv(128).decode("utf-8")
			if inp == spellme:
				score += 1
		time_thread.join()
		p2stats["hp"] -= score + int(p1stats["atk"])
		if p2stats["hp"] <= 0:
			win = 1
			player1.send(f"{p2stats['name']} was defeated, you had {p1stats['hp']} health left".encode("utf-8"))
			after_fight(win, cachehp)
			break
		elif p1stats["hp"] <= 0:
			win = 0
			player1.send("you were defeated".encode("utf-8"))
			after_fight(win, cachehp)
			break
		player1.send(f"{p1stats['name']} took f{score + int(p2stats['atk'])} damage. You have {p2stats['hp']} health".encode("utf-8"))
					
	
def p2fight(player2):
	global p2ready
	cachehp = p2stats["hp"]
	player2.send("are you ready? (wating for other players confirmation)".encode("utf-8"))
	conf = player2.recv(48).decode("utf-8")
	if "y" in conf:
		p2ready = 1
	else:
		return
	while not p2ready:
		pass
	while not p1ready:
		pass
	while True:
		spellme = words[random.randint(0, len(words) - 1)]
		score = 0
		count = random.randint(0,7 + (p2stats["spd"] // 10))
		time_thread = threading.Thread(target=timer, args=(count,))
		time_thread.start()
		while not done:
			spellme = words[random.randint(0, len(words) - 1)]
			player2.send(f"Word: {spellme}".encode("utf-8"))
			inp = player2.recv(128).decode("utf-8")
			if inp == spellme:
				score += 1
		time_thread.join()
		p1stats["hp"] -= score + int(p2stats["atk"])
		if p1stats["hp"] <= 0:
			win = 1
			player2.send(f"{p1stats['name']} was defeated, you had {p2stats['hp']} health left".encode("utf-8"))
			after_fight(win, cachehp)
			break
		elif p2stats["hp"] <= 0:
			win = 0
			player2.send("you were defeated".encode("utf-8"))
			after_fight(win, cachehp)
			break
		player2.send(f"{p1stats['name']} took f{score + int(p2stats['atk'])} damage. You have {p2stats['hp']} health".encode("utf-8"))
					
def psave(info, player):
	with open(pfile, "w") as file:
		if player == 2:
			for name, val in p2stats.items():
				file.write(f"{name}={val}\n")
		if player == 1:
			for name, val in p1stats.items():
				file.write(f"{name}={val}\n")

def timer(count):
	global done
	done = 0
	cache = 0.0
	while cache != count:
		if p1stats["hp"] <= 0:
			break
		elif p2stats["hp"] <= 0:
			break
		time.sleep(1)
		cache += 1
	done = 1

p1thread = threading.Thread(target=player1start, args=(server,))
p2thread = threading.Thread(target=player2start, args=(server,))

p1thread.start()
p2thread.start()
