from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import base64

conf_path = "/etc/keygetsrv"

if "keygetsrv" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)

if "keys.conf" not in os.listdir("/etc/keygetsrv"):
	with open(f"{conf_path}/keys.conf", "w") as file:
		file.write("")

port = int(input("port: "))

server = netcom.socket(ipv4, tcp)
server.setsockopt(netcom.SOL_SOCKET, netcom.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", port))

while True:
	server.listen(1)
	client, client_ip = server.accept()
	ack = client.recv(1024).decode("utf-8")
	if ack == "ack":
		client.send("ack".encode("utf-8"))
		try:
			to_send = ""
			cmd = client.recv(1024).decode("utf-8")
			if cmd == "key":
				with open(f"{conf_path}/keys.conf", "r") as file:
					keys = file.readlines()
					if not keys:
						client.send("no keys in file, or wrong format (name=key)".encode("utf-8"))
					else:
						for item in keys:
							keyip, keyname, key = item.split("=", 2)
							to_send += f"{keyname}\n{keyip}\n{key}\n"
						client.send(to_send.encode("utf-8"))
			elif "key" in cmd and " " in cmd:
				with open(f"{conf_path}/keys.conf", "r") as file:
					keys = file.readlines()
					if not keys:
						client.send("no keys in file, or wrong format (name=key)".encode("utf-8"))
					else:
						junk, name = cmd.split(" ", 1)
						for item in keys:
							keyip, keyname, key = item.split("=", 2)
							print(keyname)
							if name.strip() == keyname:
								print(f"found {name}")
								if "-s" not in cmd:
									to_send = f"{keyname}\n{keyip}\n{key}"
									break
								elif "-s" in cmd:
									to_send = key
									break
							else:
								to_send = "idk"
						client.send(to_send.encode("utf-8"))
			elif "download" in cmd and " " in cmd:
				with open(f"{conf_path}/keys.conf", "r") as file:
					keys = file.readlines()
					if not keys:
						client.send("no keys in file, or wrong format (name=key)".encode("utf-8"))
					else:
						junk, name = cmd.split(" ", 1)
						for item in keys:
								keyip, keyname, key = item.split("=", 2)
								if name.strip() == keyname:
									to_send = f"!file!{keyip}!ip!{keyname}!name!{key}"
									client.send(to_send.encode("utf-8"))
			elif cmd == "download":
				with open(f"{conf_path}/keys.conf", "r") as file:
					keys = file.readlines()
					if not keys:
						client.send("no keys in file, or wrong format (name=key)".encode("utf-8"))
					else:
						for item in keys:
							to_send += f"!file!all!ip!keys!name!{item}\n"
						client.send(to_send.encode("utf-8"))
			elif "upload" in cmd:
				trash, keyip, keyname, key = cmd.split(" ", 3)
				keylist = []
				with open(f"{conf_path}/keys.conf", "r") as file:
					data = file.readlines()
					for item in data:
						if "=" in item:
							keylist.append(item)
				keylist.append(f"{keyip}={keyname}={key}")
				with open(f"{conf_path}/keys.conf", "w") as file:
					for item in keylist:
						file.write(f"{item}\n")
				client.send("key uploaded".encode("utf-8"))
			
			else:
				client.send("idk what that is tbh")
		except Exception as e:
			print(e)
			client.shutdown(socket.SHUT_RDRW)
			client.close()
