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
auto = 0
auth = {"user": username, "pass": password, "ip": ipaddr, "port": port}

botnames = ["john doe", "vinny krob", "bill starch", "tim stronk", "jim giggs", "shik steam", "devin"]

level = 0
exp = 0
expreq = 20
health = 20
attack = 0
defense = 0
speed = 0
points = 0

done = 0


difflist = {"1": "pussy",
"2": "easier",
"3": "easy",
"4": "medium",
"5": "hard",
"6": "very hard",
"7": "nightmare",
"8": "impossible",
"9": "endless"
}

stats = {"hp": health, "pnt": points, "lvl": level, "xp": exp, "req": expreq, "atk": attack, "def": defense, "spd": speed}

words = ["one","into","a","seat","flip","not","unset","nail","joke","laugh","enjoy","old","eye","file","bring","love","lie","sprawl","shook","rather","involved","time","right","there","left","tell","camera","before","more","over","flee","stand","rush","friend","address","of","emergecy","guy","got","down","couple", "hunt", "run","without","help","trace","old","year","state","car", "hands", "arrived", "anyone", "on", "this", "fall","high","try","burn","toss","lap","cant","did","do","too","to","two","flow","tan","brain","glove","county","had","come","here","room","work"]

if "oneturnfight" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)
if "local_scores.conf" not in os.listdir(conf_path):
	with open(f"{conf_path}/local_scores.conf", "w") as file:
		file.write("")
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
		inp = input("(main menu) >>> ")
		xcute = cmds.get(inp)
		if xcute:
			if "fight" in inp:
				for val, name in difflist.items():
					print(f"{val}. {name}")
				inp = input("Select difficulty (press enter for default): ")
				if inp not in "1234567890":
					continue
				if not inp:
					xcute(None)
				else:
					xcute(difflist[inp.strip()])
			else:
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
			inp = input("(online) >>> ")
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

def localfight(diff):
	global count
	
	finalright = 0
	finalwrong = 0
	
	cachehp = stats["hp"]
	bonus = 0
	ehealth = 0
	eattack = 0
	edefense = 0
	elevel = 0
	difftime = 0
	diffcount = 0
	if diff == "pussy":
		difftime = -14
		diffcount = 3
		ehealth -= 10
		eattack -= 5
		edefense -= 5
	elif diff == "easier":
		difftime = -12
		diffcount = 2
		ehealth -= 7
		eattack -= 3
		edefense -= 3
	elif diff == "easy":
		difftime = -9
		diffcount = 1
		ehealth -= 5
		eattack -= 1
		edefense -= 1
	elif diff == "medium":
		difftime = -4
		ehealth += 3
		eattack += 2
		edefense += 2
	elif diff == "hard":
		difftime = 2
		ehealth += 5
		eattack += 3
		edefense += 3
	elif diff == "very hard":
		difftime = 5
		diffcount = -1
		ehealth += 10
		eattack += 4
		edefense += 4
	elif diff == "nightmare":
		difftime = 7
		diffcount = -1
		ehealth += 15
		eattack += 5
		edefense += 5
	elif diff == "impossible":
		difftime = 9
		diffcount = -2
		ehealth += 25
		eattack += 7
		edefense += 7
	ename = botnames[random.randint(0, len(botnames) - 1)]
	hostile = {"name": ename,"hp": ehealth, "atk": eattack, "def": edefense, "lvl": elevel, "diff": difftime, "bonus": bonus}
	hostile["hp"] += random.randint(int(stats["hp"]) - 5, int(stats["hp"]) + 20)
	hostile["atk"] += random.randint(int(stats["atk"]) - 3, int(stats["atk"]) + 5)
	hostile["def"] += random.randint(int(stats["def"]) - 3, int(stats["def"]) + 5)
	hostile["lvl"] += random.randint(int(stats["lvl"]) - 3, int(stats["lvl"]) + 5)
	hostile["bonus"] += random.randint(0, int(hostile["lvl"]) + 15)
	
	if hostile["atk"] <= 0:
		hostile["atk"] = 1
	if hostile["def"] <= 0:
		hostile["def"] = 0
	if hostile["lvl"] <= 0:
		hostile["lvl"] = 0
	if diff == "endless":
		ename = "god"
		hostile["atk"] = 1
		hostile["def"] = 0
		hostile["lvl"] = 0
		hostile["hp"] = 10000000000
	print(f"You are facing: {ename}")
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
		count = random.randint(0,4 + diffcount + (stats["spd"] // 10))
		time_thread = threading.Thread(target=timer, args=(count,))
		time_thread.start()
		hostile_thread = threading.Thread(target=hostilefight, args=(hostile,))
		hostile_thread.start()
		while not done:
			spellme = words[random.randint(0, len(words) - 1)]
			inp = input(f"Word: {spellme}\n(fight) >>> ")
			if auto:
				inp = spellme
			if inp == spellme:
				score += 1
				finalright += 1
			else:
				finalwrong += 1
		time_thread.join()
		hostile["bonus"] += score
		hostile["hp"] -= score + int(stats["atk"])
		if hostile["hp"] <= 0:
			hostile_thread.join()
			win = 1
			print(f"{hostile['name']} was defeated, you had {stats['hp']} health left")
			after_fight(win, hostile, cachehp, finalright, finalwrong)
			break
		elif stats["hp"] <= 0:
			hostile_thread.join()
			win = 0
			print(f"you were defeated. Tallies:\nWords right: {finalright}\nWords wrong: {finalwrong}\nHealth: {stats['hp']}\nHostiles health: {hostile['hp']}")
			after_fight(win, None, cachehp, finalright, finalwrong)
			break
		print(f"{hostile['name']} took f{score + int(stats['atk'])} damage. You have {stats['hp']} health")

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
				if hostile["diff"] < 0:
					waittime = random.randint(12 - random.randint(hostile["diff"], 0), 29 - random.randint(hostile["diff"], 0)) / 10
				else:
					waittime = random.randint(12 - random.randint(0, hostile["diff"]), 22 - random.randint(0, hostile["diff"])) / 10

				time.sleep(waittime)
			if hostile["hp"] <= 0 or stats["hp"] <= 0:
				break
			score += 1
			if random.randint(0,1) == 1:
				score -= 1
			hostile["bonus"] += score
			stats["hp"] -= score + int(hostile["atk"])
		
def after_fight(status, reward, cachehp, right, wrong):
	cache = 0
	stats["hp"] = cachehp
	if status:
		for trash, val in reward.items():
			if trash == "name" or trash == "diff":
				continue
			if val < 0:
				val *= -1
			cache += val
		stats["xp"] += cache
		savestat()
		print(f"youve gained {cache} exp")
	with open(f"{conf_path}/local_scores.conf", "r") as file:
		data = file.readlines()
	with open(f"{conf_path}/local_scores.conf", "w") as file:
		for item in data:
			if "r" in item:
				item = item.strip("r")
				right = right + int(item)
			elif "w" in item:
				item = item.strip("w")
				wrong = wrong + int(item)
		file.write(f"r{right}\nw{wrong}")
	
		
		
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
			file.write(f"{name}={str(val)}\n")
def getscore():
	with open(f"{conf_path}/local_scores.conf", "r") as file:
		data = file.readlines()
		if not data:
			return
		for item in data:
			if "r" in item:
				r = item.strip('r').strip('\n')
				print(f"Right: {r}")
			elif "w" in item:
				w = item.strip('w')
				print(f"Wrong: {w}")
		numscore = (int(r) / int(w)) * 10000
		print(f"Rating: {numscore // 1}")
		if numscore < 25000:
			score = "Too low to be measured"
		if numscore > 25000:
			score = "E"
		if numscore > 35000:
			score = "F"
		if numscore > 50000:
			score = "D"
		if numscore > 850000:
			score = "C"
		if numscore > 100000:
			score = "B"
		if numscore > 150000:
			score = "A"
		if numscore > 200000:
			score = "S"
		if numscore > 300000:
			score = "Z"
		if numscore > 500000:
			score = "God"
		if int(r) < 100:
			score = "Too low to be measured"
		print(f"Grade: {score}")

def helpy():
	for name, val in cmds.items():
		print(name)
def getstat():
	for name, val in stats.items():
		print(f"{name}: {val}")
cmds = {"fight": localfight, "login": online, "help": helpy, "score": getscore, "stats": getstat}

main()
