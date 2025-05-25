#!/usr/bin/env python3

import requests
import time
success = 2

link0 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/Universal%20Tools/updater.py"
link1 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zweather/guiweather.py"
link2 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/zbrowse/zbrowse.py"
link3 = "https://raw.githubusercontent.com/Zin-ful/zin-minimal-suite/refs/heads/main/main.py"

numbertoname = {"0": "updater", "1": "guiweather", "2": "zbrowse", "3": "main"}
apps_dict = {"updater": link0, "guiweather": link1, 
	     "zbrowse": link2, "main": link3}

print("\nTool Version: 1.0\n\nWelcome to the special application tool.")
time.sleep(2)
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
	
	

