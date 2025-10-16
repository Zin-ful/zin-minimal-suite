import os
import socket as netcom
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import threading as task
import tarfile
import time

head_sze = 100
port = 41742
ip = "0.0.0.0"
chnk_sze = 1024
passwd = "admin"
verbose = "1"
logging = "1"
config_path = "/etc/zapp_srvr"
app_locations = "/etc/zapp_srvr/programs"
cache = "/etc/zapp_srvr/cache"
server = netcom.socket(ipv4, tcp)
server.bind((ip, port))

attr_dict = {"verbose": verbose, "logging": logging}

"""main actions"""
def install(client_socket, name):
	try:
		if name in os.listdir(app_locations):
			compress(name)
			with open(f"{cache}/{name}", "rb") as file:
				file.seek(0, 2)
				file_size = file.tell()
				file.seek(0)
				print(f"sending data {name} size = {str(len(name)).zfill(head_sze)}")
				client_socket.send(str(len(name)).zfill(head_sze).encode("utf-8"))
				client_socket.send(name.encode("utf-8"))
				client_socket.send((str(file_size).zfill(head_sze)).encode("utf-8"))
				print(f"sending file {name} size = {(str(file_size).zfill(head_sze))}")
				while True:
					chunk = file.read(chnk_sze)
					if not chunk:
						break
					client_socket.sendall(chunk)
				cleanup(name)
				return 1
		else:
			err = "err: App is not found. To see avaliable apps, use list-aval"
			client_socket.send(str(len(err)).zfill(head_sze).encode("utf-8"))
			client_socket.send(err.encode("utf-8"))
			return print("invalid request, app not found")
	except Exception as e:
		print(e)
def list_update(client_socket, *arg):
	apps = ""
	with open(f"{config_path}/app_list.txt", "r") as file:
		for i in file.readlines():
			apps += f"{i}\n"
	client_socket.send(apps.encode("utf-8"))
	return 1

def list_apps(client_socket, *arg):
	result = ""
	for i in os.listdir(app_locations):
		result += f"{i}\n"
	client_socket.send(result.encode("utf-8"))

def update(client_socket, *arg):
	return

action_dict = {"install": install, "listretr": list_update, "update": update, "list-aval": list_apps,}

"""main"""
def main(client_socket, addr):
	client_socket.send(f"connected!|{str(chnk_sze)}".encode("utf-8"))
	while True:
		action = client_socket.recv(128)
		if action:
			print(action)
			action = action.decode("utf-8")
			if " " in action:
				action, flag = action.split(" ", 1)
			else:
				flag = action
			xcute = action_dict.get(action.strip())
			if xcute:
				status = xcute(client_socket, flag.strip())
				if status:
					print("Command success!")
					log("Command success!")
				else:
					print("Error occured")
					log("Error occured")
			else:
				client_socket.send("##invalid command".encode("utf-8"))
	
	
	
"""utils"""
def compress(name):
	with tarfile.open(f"{cache}/{name}", "w:gz") as tar:
		tar.add(f"{app_locations}/{name}", arcname=os.path.basename(f"{app_locations}/{name}"))
def cleanup(name):
	os.remove(f"{cache}/{name}")

def uncompress(name):
	with tarfile.open(f"{cache}/{name}", 'r:gz') as tar:
		tar.extractall(path=app_locations)

def log(item):
	with open(f"{config_path}/log.txt", "a") as file:
		file.write(f"{item}\n")

def setup():
	try:
		with open(f"{config_path}/zserv.conf", "r") as file:
			for line in file.readlines():
				word, num = line.split("=")
				attr_dict[word.strip()] = num.strip()			
	except Exception as e:
		#print(e)
		print("Looks like this is your first time running zapp. I will create the directories and config files.")	
		print(f"Generating the config directory")
		os.makedirs(config_path, exist_ok=True)
		print(f"Generating the programs directory")
		os.makedirs(app_locations, exist_ok=True)
		print(f"Generating the cache directory")
		os.makedirs(cache, exist_ok=True)
		print("Generating config..")
		with open(f"{config_path}/zserv.conf", "a") as file:
			print("Writing attribute: verbose")
			file.write(f"verbose = {verbose}\n")
			print("Writing attribute: logging")
			file.write(f"logging = {logging}\n")
		print("generating app list..")
		with open(f"{config_path}/app_list.txt", "w") as file:
			file.write("")
			print("wrote nothing to file. Either add apps manually or use zpush")
setup()

while True:
    try:
        server.listen(10)
        print(f"server listening on ip: {ip} and port {port}")
        client_socket, addr = server.accept()
        client_thread = task.Thread(target=main, args=(client_socket, addr))
        client_thread.start()
    except Exception as e:
        print(f"threading failed: {e}")
