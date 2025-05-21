#!/usr/bin/env python3

import requests
import time
link0 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/Universal%20Tools/updater.py"
link1 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zweather/weathertool.py"
link2 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zweather/weathertool-backgroundproc.py"
link3 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zweather/linux-weathertool.py"
link4 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zbrowse/zbrowse.py"
link5 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/ztalk/ztext/message_intelligent.py"
link6 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/ztalk/ztext_srvr/message_server.py"
link7 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zfile/client/client.py"
link8 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zfile/server/server.py"
link9 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zfile/server/handle_cmd.py"
link10 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zapp/server/zapp_server.py"
link11 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zapp/client/zget.py"
link12 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/Universal%20Tools/Uniconfig.py"
link13 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/Universal%20Tools/Unihelp.py"
numbertoname = {"0": "Update Tool", "1": "Weather Tool", "2": "Weather Tool (Background)", "3": "Weather Tool (linux)", "4": "File Browser", "5": "Messenger", "6": "Messenger Server", "7": "Cloud Storage Client", "8": "Cloud Storage Server (Depends on handler)", "9": "Handler", "10":"Application Server", "11": "Application Retreiver", "12": "Universal Helper", "13": "Universal Configuration Tool"}
apps_dict = {"Update Tool": link0, "Weather Tool": link1, 
	     "Weather Tool (Background)": link2, "Weather Tool (linux)": link3, 
	     "File Browser": link4, "Messenger": link5, "Messenger Server": link6, 
	     "Cloud Storage Client": link7, "Cloud Storage Server (Depends on handler)": link8, 
	     "Handler": link9, "Application Server": link10, "Application Retreiver": link11,
	     "Universal Helper": link12, "Universal Configuration Tool": link13}

print("Tool Version: 1.6\nWelcome to the emergency application tool. Or E.A.T.\nThis tool has been called because A: You are using it directly\nB: The application installer has failed to connect to a server\nOr C: The application installer does not exist.\nLets go ahead and look at your options for install.\nWait about 10 seconds while i grab those.")
time.sleep(10)
m = 0
for name, trash in apps_dict:
	print(f"{m}. {name}")
print("What would you like to retrieve?")

def updateme(link, name):
	response = requests.get(link)
	errors = response.raise_for_status()
	if response.status_code == 200:
		with open(name, "wb") as file:
			file.write(response.content)
	elif response.status_code == 400:
		print(f"\n****Err: {response.status_code}, code 400 points to the link being incorrect or it could be a server-side issue")
	elif response.status_code == 404:
		print(f"\n****Err: {response.status_code}, code 404 points to the link/file being unavalible or the site is down/no longer maintained")
	elif response.status_code == 408:
		print(f"\n****Err: {response.status_code}, code 408 points to your request not reaching the site before it timed out")
	else:
		print(f"\n****Err: {response.status_code}")
	print("updated!!")
while True:
	inp = input(">>> ")
	if "exit" in inp:
		exit()
	for i, name in numbers_list:
		if inp in i:
			inp = int(inp)
	

