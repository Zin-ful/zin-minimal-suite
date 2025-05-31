#!/usr/bin/env python3

import requests
import time
success = 2

link0 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/Universal%20Tools/updater.py"
link1 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zweather/weathertool.py"
link2 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zweather/weathertool-backgroundproc.py"
link3 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zweather/linux-weathertool.py"
link4 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zbrowse/zbrowse.py"
link5 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/ztalk/ztext/msg.py"
link6 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/ztalk/ztext_srvr/messagesrv.py"
link7 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zfile/client/client.py"
link8 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zfile/server/server.py"
link9 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zfile/server/handle_cmd.py"
link10 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zapp/server/zapp_server.py"
link11 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zapp/client/zget.py"
link12 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/Universal%20Tools/uniconfig.py"
link13 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/Universal%20Tools/unihelp.py"
link14 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/znet/keyget.py"
link15 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/znet/keygetsrv.py"
link16 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zbrowse/usbctrl.py"
link17 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/games/oneturnfight.py"



numbertoname = {"0": "updater", "1": "weathertool", "2": "weathertoolbg", "3": "linux-weathertool", 
		"4": "browse", "5": "msg", "6": "msgsrv", "7": "clientstore", "8": "serverstore", 
		"9": "handle_cmd", "10":"zapp", "11": "zget", "12": "unihelp", "13": "uniconf", "14": "keyget", "15":"keygetsrv", "16":"usbctrl", "17":"oneturnfight"}
apps_dict = {"updater": link0, "weathertool": link1, 
	     "weathertoolbg": link2, "linux-weathertool": link3, 
	     "browse": link4, "msg": link5, "msgsrv": link6, 
	     "clientstore": link7, "serverstore": link8, 
	     "handle_cmd": link9, "zapp": link10, "zget": link11,
	     "unihelp": link12, "uniconf": link13, "keyget": link14, "keygetsrv": link15, "usbctrl":link16 , "oneturnfight": link17}

print("\nTool Version: 1.6\n\nWelcome to the emergency application tool. Or E.A.T.\nThis tool has been called because\nA: You are using it directly\nB: The application installer has failed to connect to a server\nOr C: The application installer does not exist.\nLets go ahead and look at your options for install.\nWait about 10 seconds while i grab those.\n")
time.sleep(12)
m = 0
for name, trash in apps_dict.items():
	print(f"{m}. {name}")
	m += 1
print("What would you like to retrieve?")

def updateme(link, name):
	global success
	response = requests.get(link)
	errors = response.raise_for_status()
	if response.status_code == 200:
		with open(name+".py", "wb") as file:
			file.write(response.content)
	elif response.status_code == 400:
		print(f"\n****Err: {response.status_code}, code 400 points to the link being incorrect or it could be a server-side issue")
		return 0
	elif response.status_code == 404:
		print(f"\n****Err: {response.status_code}, code 404 points to the link/file being unavalible or the site is down/no longer maintained")
		return 0
	elif response.status_code == 408:
		print(f"\n****Err: {response.status_code}, code 408 points to your request not reaching the site before it timed out")
		return 0
	else:
		print(f"\n****Err: {response.status_code}")
		return 0
	print("updated!!")
	return 1
while True:
	inp = input(">>> ")
	if "exit" in inp:
		exit()
	for i, name in numbertoname.items():
		if inp in i:
			success = updateme(apps_dict[numbertoname[inp]], numbertoname[inp])
	for name, trash in apps_dict.items():
		if inp == name:
			success = updateme(apps_dict[inp], name)
	if success == 1:
		break
	elif success == 2:
		print("Sorry but i dont think thats an option.")
	elif not success:
		print("Seems like an error has occurred, try again please")
	
	

