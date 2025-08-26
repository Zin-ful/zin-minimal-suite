from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
from random import randint
import os
import base64
import threading as task
conf_path = "/etc/keygetsrv"
wg_number = 0
flags = {"-w": "*%_@"}
if "keygetsrv" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)

if "title.conf" not in os.listdir("/etc/keygetsrv"):
	with open(f"{conf_path}/title.conf", "w") as file:
		file.write("wg")
		wg_title = "wg"
else:
	with open (f"{conf_path}/title.conf", "r") as file:
		wg_title = file.read()
		wg_title = wg_title.strip()

if "wireguard" not in os.listdir("/etc"):
	print("wireguard is not installed.")
	exit()
else:
	print("wireguard is installed")
	wg_dir = os.listdir("/etc/wireguard")
	if not wg_dir:
		print("wireguard is not configured.")
		exit()
	for item in wg_dir:
		if wg_title in item:
			while True:
				print(f"{wg_title}{wg_number}.conf")
				if item == f"{wg_title}{wg_number}.conf":
					break
				conf_number += 1
				if conf_number >= 100:
					print("you do not have a wireguard configuration file made.\nIf it is under an alias that is not wg0-100, please edit the configuration file at /etc/keygetsrv")
					exit()

#port = int(input("port: "))
port = 12345
server = netcom.socket(ipv4, tcp)
print("socket created")
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
print("set socket options")
server.bind(("0.0.0.0", port))
print(f"bound to {port}")

def make_config(client, data):
	return

def helpy(client, data):
	return "Commands are:\nput [name] [ip] [key]\nget [name]\nmkconf\ncheck [name]\n"
def upload(client, data):
	return

def download(client, name): #format properly for client, see file in home
	aval_keys = []
	aval_ips = []
	with open(f"/etc/wireguard/{wg_title}{wg_number}.conf", "r") as file:
		peers = file.readlines()
		i = 0
		for item in peers:
			print(item)
			if "[Peer]" in item:
				if "!!None" in item:
					print("avaliable peer found")
					cache, key = peers[i + 1].split("=", 1)
					print("key found")
					key = key.strip()
					cache, ip = peers[i + 2].split("=", 1)
					print("ip found")
					ip = ip.strip()
					aval_keys.append(key)
					aval_ips.append(ip)
					print("peer added to list")
			i += 1
		if not aval_keys or not aval_ips:
			return "No peer with that name found."
		selection = randint(0, len(aval_keys) - 1)
		client.send(f"Avaliable key and ip found: {aval_keys[selection]}:{aval_ips[selection]}\ndo you accept?".encode("utf-8"))
		response = client.recv(1024).decode("utf-8")
		if "y" in response:
			conf_file= ""
			i = 0
			for item in peers:
				if "[Peer]" in item:
					break
				i += 1
			j = 0
			for item in peers:
				conf_file += item
				j += 1
				if j >= i:
					break
			client.send(f"{flags['-w']+conf_file}".encode("utf-8"))
		else:
			return "discarding..."
			


def view(client, data):
	with open(f"/etc/wireguard/{wg_title}{wg_number}.conf", "r") as file:
		return file.read()

def verify(client, name):
	with open(f"/etc/wireguard/{wg_title}{wg_number}.conf", "r") as file:
		for item in file.readlines():
			print(item)
			if "[Peer]" in item:
				cache, user = item.split("#")
				if name.lower() in user.lower():
					return "That name/device is active."
		return "No peer with that name found."

def sort(request):
	if "get" in request:
		return "get", None
	elif "put" in request:
		i = 0
		for item in request:
			if item == " ":
				i += 1
		if i > 3:
			return 0, "Too many arguments, the syntax is 'put name ip key"
		elif i < 3:
			return 0, "Too few arguments, the syntax is 'put name ip key'"
		request, data = request.split(" ", 1)
		return request, data
	elif "check" in request:
		if " " not in request:
			return 0, "Invalid syntax, provide the name you would like to check"
		request, name = request.split(" ", 1)
		return request, name
	elif "mkconf" in request:
		return "mkconf", None
	elif "help" in request:
		return "help", None
	else:
		return 0, "sorry, that isnt a command"
	

def client_start(client):
	while True: 
		if not client:
			return print("client data not passed, returning")
		try:
			print("request...")
			request = client.recv(1024).decode("utf-8")
			print(f"client said: {request}")
			if request:
				request, response = sort(request)
				for name, function in cmd_dict.items():
					if request == name:
						response = function(client, response)
						break
			if response:
				client.send(response.encode("utf-8"))
		except Exception as e:
			print(e)
			print("returning to main thread")
			return


def server_init():
	while True:
		try:
			server.listen(20)
			client, client_ip = server.accept()
			print("client accepted, acking")
			client.send("ack".encode("utf-8"))
			ack = client.recv(3).decode("utf-8")
			print(f"acked '{ack}' starting thread")
			thread_client = task.Thread(target=client_start, args=[client])
			thread_client.start()
		except Exception as e:
			print(e)

cmd_dict = {"help": helpy, "put": upload, "get": download, "mkconf": make_config, "check": verify, "list": view}

server_init()