from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
from random import randint
import os
import base64
import threading as task
import subprocess as proc

conf_path = "/etc/keygetsrv"
flags = {"-w": "*%_@"}



#port = int(input("port: "))
port = 10592
server = netcom.socket(ipv4, tcp)
print("socket created")
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
print("set socket options")
server.bind(("0.0.0.0", port))
print(f"bound to {port}")

def init():
	wg_number = 0
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
			print("issues found, starting repair...")
			if not fix_wg():
				print("repair failure, exiting...")
				exit()
		for item in wg_dir:
			if wg_title in item and ".swp" not in item:
				while True:
					print(f"{item} = {wg_title}{wg_number}.conf")
					if item == f"{wg_title}{wg_number}.conf":
						break
					wg_number += 1
	return wg_title, wg_number

def fix_wg():
	inp = input("Issues in configuration file found, this program uses default wg settings\ndo not overwrite your own files. continue to wireguard repair? there is no going back.\n>>> ")
	if "y" not in inp:
		return 0
	path = "/etc/wireguard/"
	print("generating private key")
	privkey = proc.run(["wg", "genkey"], capture_output=True, text=True)
	privkey = privkey.stdout
	with open(path+"private.key", "w") as file:
		file.write(privkey)
	print(str(privkey)+"\n")
	print("generating public key")
	pubkey = proc.run(["wg", "pubkey"], input=privkey, capture_output=True, text=True)
	pubkey = pubkey.stdout
	print(str(pubkey)+"\n")
	with open(path+"public.key", "w") as file:
		file.write(pubkey)
	print("keys written.")
	print("generating wg0.conf in /etc/wireguard")
	with open(path+"wg0.conf", "w") as file:
		port = input("Your router should have a row added in your port map with an IP address and port\nEnter the port now: ")
		server_ip = input("Now enter the IP Address: ")
		file.write(f"[Interface]\nAddress = 10.0.0.1/24\nSaveConfig = false\nPreUp = iptables -A FORWARD -i %i -j ACCEPT\nPostDown = iptables -D FORWARD -i %i -j ACCEPT\nListenPort = {port}\nPrivateKey = {privkey}\n#!!PublicKey = {pubkey}\n#!!ServerIP = {server_ip}\n\n")
	print("file generated.")
	inp = input("Would you like to generate client key pairs for download?\n>>> ")
	if "y" not in inp:
		print("returning to init...")
		return 1
	
	with open(path+"wg0.conf", "r") as file:
		conf_file = file.read()
		conf_file += "\n\n"
	i = 2
	while i < 253:
		print(f"generating key-pair {i}")
		privkey = proc.run(["wg", "genkey"], capture_output=True, text=True)
		privkey = privkey.stdout
		pubkey = proc.run(["wg", "pubkey"], input=privkey, capture_output=True, text=True)
		pubkey = pubkey.stdout
		conf_file += f"\n[Peer]#!!None\nPublicKey = {pubkey}\n#!!PrivateKey = {privkey}\nAllowedIPs = 10.0.0.{i}/32\n"
		i += 1	
	with open(path+"wg0.conf", "w") as file:
		file.write(conf_file)
	print("finished repair, continuing start..")
	return 1

def make_config(client, data):
	return

def helpy(client, data):
	return "Commands are:\nget [name]\ncheck [name]\n"

def download(client, name):
	aval_pubkeys = []
	aval_privkeys = []
	aval_ips = []
	with open(f"/etc/wireguard/{wg_title}{wg_number}.conf", "r") as file:
		peers = file.readlines()
		i = 1
		for item in peers:
			print(item)
			if "[Peer]" in item:
				if "!!None" in item:
					print("avaliable peer found")
					j = 0
					while peers[i + j] == '\n':
						j += 1
					cache, pubkey = peers[i + j].split("=", 1)
					print("pubkey found")
					pubkey = pubkey.strip()
					j += 1
					while peers[i + j] == '\n':
						j += 1
					cache, privkey = peers[i + j].split("=", 1)
					print("privkey found")
					privkey = privkey.strip()
					j += 1
					while peers[i + j] == '\n':
						j += 1
					cache, ip = peers[i + j].split("=", 1)
					print("ip found")
					ip = ip.strip().strip("/32")

					aval_pubkeys.append(pubkey)
					aval_privkeys.append(privkey)
					aval_ips.append(ip)
					print("peer added to list")
			i += 1
		if not aval_pubkeys:
			return "No peer with that name found."
		selection = randint(0, len(aval_pubkeys) - 1)
		client.send(f"Avaliable key and ip found:\n{aval_pubkeys[selection]}\n{aval_ips[selection]}\ndo you accept?".encode("utf-8"))
		response = client.recv(1024).decode("utf-8")
		client.send("To make sure your key and ip arent reused, make a username, ID, anything really\nso we can add it to our conf file to prevent selections\nfor example: sarahs iphone.\nenter your username now:".encode("utf-8"))
		name = client.recv(1024).decode("utf-8")
		if "y" in response:
			server_ip = "#!!ServerIP = "
			server_pubkey = "#!!PublicKey = "
			for item in peers:
				if server_ip in item:
					server_ip = item.strip(server_ip).strip("\n")
				if server_pubkey in item:
					server_pubkey = item.strip(server_pubkey)
				if "ListenPort =" in item:
					server_port = item.strip("ListenPort = ").strip("\n")
			conf_file = f"#!!Keys={aval_pubkeys[selection]}&{aval_privkeys[selection]}:[Interface]\nPrivateKey = {aval_privkeys[selection]}\nAddress = {aval_ips[selection]}/24\n\n[Peer]\nPublicKey = {server_pubkey}\nAllowedIPs = 10.0.0.0/24\nEndpoint = {server_ip}:{server_port}\nPersistentKeepalive = 25"
			client.send(f"{flags['-w']+conf_file}".encode("utf-8"))
			i = 0
			for item in peers:
				if aval_pubkeys[selection] in item:
					while "[Peer]" not in peers[i]:
						i -= 1
					peers[i] = "[Peer]" + "#!!"+name+"\n"
					break
				i += 1
			with open("/etc/wireguard/wg0.conf", "w") as file:
				for item in peers:
					file.write(item)
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
			if not request:
				return print("client left, returning to main thread")
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
			client.close()
			return

def server_init():
	while True:
		try:
			client, client_ip = server.accept()
			print("client accepted, acking")
			client.send("ack".encode("utf-8"))
			ack = client.recv(3).decode("utf-8")
			print(f"acked '{ack}' starting thread")
			thread_client = task.Thread(target=client_start, args=[client])
			thread_client.start()
		except Exception as e:
			print(e)

cmd_dict = {"help": helpy, "get": download, "mkconf": make_config, "check": verify, "list": view}

wg_title, wg_number = init()

print("listening...")
server.listen(20)
			

server_init()