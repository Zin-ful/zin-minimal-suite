from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import time
import random
import threading
import base64
conf_path = "/etc/oneturnfight"

username = ""
password = ""
ipaddr = None
port = None

auth = {"user": username, "pass": password, "ip": ipaddr, "port": port}

level = 0
exp = 0
expreq = 0
health = 20
attack = 0
defense = 0
speed = 0
points = 0

done = 0

stats = {"hp": health, "pnt": points, "lvl": level, "xp": exp, "req": expreq, "atk": attack, "def": defense, "spd": speed}

words = ["one","into","a","seat","flip","not","unset","nail","joke","laugh","enjoy","old","eye","file","bring","love","lie","sprawl","shook","rather","involved","time","right","there","left","tell","camera","before","more","over","flee","stand","rush","friend","address","of","emergecy","guy","got","down","couple", "hunt", "run","without","help","trace","old","year","state","car", "hands", "arrived", "anyone", "on", "this", "fall","high","try","burn","toss","lap","cant","did","do","too","to","two","flow","tan","brain","glove","county","had","come","here","room","work"]

if "oneturnfight" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)
if "local_player.conf" not in os.listdir(conf_path):
	with open(f"{conf_path}/local_player.conf", "w") as file:
		for name, val in stats.items():
			file.write(f"{name}={val}\n")
else:
	with open(f"{conf_path}/local_player.conf", "r") as file:
		load_stat = file.readlines()
		for item in load_stat:
			item = item
			name, val = item.split("=")
			stats[name] = int(val)
			
if "login.conf" not in os.listdir(conf_path):
	with open(f"{conf_path}/login.conf", "w") as file:
		for name, val in auth.items():
			file.write(f"{name}={val}\n")
else:
	with open(f"{conf_path}/login.conf", "r") as file:
		load_auth = file.readlines()
		for item in load_auth:
			item = item
			name, val = item.split("=")
			print(f"{name}={val}")
			auth[name] = val	
		
			
def main():
	print("Welcome to One Turn Fight, either fight locally or fight online!\n\nType 'login' to go online, otherwise type 'help' for more inormation")
	while True:
		inp = input(">>> ")
		xcute = cmds.get(inp)
		if xcute:
			xcute()


def online():
	server = netcom.socket(ipv4, tcp)
	if not auth["ip"]:
		auth["ip"] = input("enter server ip address: ")
	if not auth["port"]:
		auth["port"] = input("enter server port: ")
	server.connect((auth["ip"], int(auth["port"])))
	server.send("ack".encode("utf-8"))
	ack = server.recv(1024).decode("utf-8")
	if ack == "ack":
		server.send("login".encode("utf-8"))
		firstmsg = server.recv(48).decode("utf-8")
		print(firstmsg)
		while True:
			inp = input(">>> ")
			server.send(inp.encode("utf-8"))
			srvresponse = server.recv(1024).decode("utf-8")
			print(srvresponse)
			if "Word: " in srvresponse:
				srvresponse = server.recv(1024).decode("utf-8")
				print(srvresponse)


		
def timer(count):
	global done
	done = 0
	cache = 0.0
	while cache != count:
		if stats["hp"] <= 0:
			break
		time.sleep(1)
		cache += 1
	done = 1

def localfight():
	global count
	
	cachehp = stats["hp"]
	
	ename = "john doe"
	ehealth = 0
	eattack = 0
	edefense = 0
	elevel = 0
	
	hostile = {"name": ename,"hp": ehealth, "atk": eattack, "def": edefense, "lvl": elevel}
	hostile["hp"] = random.randint(int(stats["hp"]) - 5, int(stats["hp"]) + 10)
	hostile["atk"] = random.randint(int(stats["atk"]) - 3, int(stats["atk"]) + 5)
	hostile["def"] = random.randint(int(stats["def"]) - 3, int(stats["def"]) + 5)
	hostile["lvl"] = random.randint(int(stats["lvl"]) - 3, int(stats["lvl"]) + 5)
	
	if hostile["atk"] <= 0:
		hostile["atk"] = 1
	if hostile["def"] <= 0:
		hostile["def"] = 0
	if hostile["lvl"] <= 0:
		hostile["lvl"] = 0
	for nm, val in hostile.items():
		print(val)
	time.sleep(1)
	print("Ready?")
	time.sleep(1)
	print("3..")
	time.sleep(1)
	print("2..")
	time.sleep(1)
	print("1..")
	time.sleep(1)
	while True:
		spellme = words[random.randint(0, len(words) - 1)]
		score = 0
		count = random.randint(0,7 + (stats["spd"] // 10))
		time_thread = threading.Thread(target=timer, args=(count,))
		time_thread.start()
		hostile_thread = threading.Thread(target=hostilefight, args=(hostile,))
		hostile_thread.start()
		while not done:
			spellme = words[random.randint(0, len(words) - 1)]
			inp = input(f"Word: {spellme}\n>>> ")
			if inp == spellme:
				score += 1
		time_thread.join()
		hostile["hp"] -= score + int(stats["atk"])
		if hostile["hp"] <= 0:
			hostile_thread.join()
			win = 1
			print(f"{hostile['name']} was defeated, you had {stats['hp']} health left")
			after_fight(win, hostile, cachehp)
			break
		elif stats["hp"] <= 0:
			hostile_thread.join()
			win = 0
			print("you were defeated")
			after_fight(win, None, cachehp)
			break
		print(f"{hostile['name']} took f{score + int(stats['atk'])} damage. You hace {stats['hp']} health")

def hostilefight(hostile):
	while True:
		if hostile["hp"] <= 0 or stats["hp"] <= 0:
			break
		spellme = words[random.randint(0, len(words) - 1)]
		score = 0
		while not done:
			if hostile["hp"] <= 0 or stats["hp"] <= 0:
				break
			spellme = words[random.randint(0, len(words) - 1)]
			for i in spellme:
				if hostile["hp"] <= 0 or stats["hp"] <= 0:
					break
				waittime = random.randint(12, 18) / 10
				time.sleep(waittime)
			if hostile["hp"] <= 0 or stats["hp"] <= 0:
				break
			score += 1
			if random.randint(0,1) == 1:
				score -= 1
			stats["hp"] -= score + int(hostile["atk"])
		
def after_fight(status, reward, cachehp):
	cache = 0
	stats["hp"] = cachehp
	if status:
		for trash, val in reward.items():
			if trash == "name" or trash == "hp":
				continue
			cache += val
		stats["xp"] += cache
		savestat()
		print(f"youve gained {cache} exp")
		
def savestat():
	if stats["xp"] >= stats["req"]:
		stats["lvl"] += 1
		stats["req"] += int(stats["req"] ** 1.1)
		stats["xp"] -= stats["xp"] 
		stats["pnt"] += 1
		
		stats["hp"] += stats["lvl"] ** 2
		stats["atk"] += stats["lvl"]
		stats["def"] += stats["lvl"]
		stats["spd"] += stats["lvl"]
		
		print("Leveled up!")
	with open(f"{conf_path}/local_player.conf", "w") as file:
		for name, val in stats.items():
			file.write(f"{name}={str(val)}\n".encode("utf-8"))
		
cmds = {"fight": localfight, "login": online}

main()
