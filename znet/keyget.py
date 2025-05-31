from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import base64

conf_path = "/etc/keyget"

if "keyget" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)
	
server = netcom.socket(ipv4, tcp)

ip = input("IP Addr: ")
port = input("Port Number: ")

server.connect((ip, int(port)))
server.send("ack".encode("utf-8"))
ack = server.recv(1024).decode("utf-8")
if ack == "ack":
	while True:
		inp = input(">>> ")
		if "upload" in inp:
			key = None
			print("format to send keys:\n ipaddr name pathtofile/key")
			ipaddr, name, path = inp.split(" ", 3)
			if "/" in path:
				with open(path, "r") as file:
					key = file.read()
					if not key:
						print("nothing in file")
						continue
			else:
				key = path
			if key:
				server.send(f"{inp} {ipaddr} {name} {key}".encode("utf-8"))
			srvresponse = server.recv(1024).decode("utf-8")
			if srvresponse:
				print(srvresponse)
				continue
			else:
				print("no data recived from server")
				continue
		server.send(inp.encode("utf-8"))
		srvresponse = server.recv(1024).decode("utf-8")
		if "!file!" in srvresponse:
			ip = srvresponse.strip("!file!")
			ip, name = ip.split("!ip!")
			name, data = name.split("!name!")
			print(f"{ip}\n{name}\nfile downloaded")
			with open(name+".txt", "w") as file:
				file.write(data)
		else:
			print(srvresponse)
