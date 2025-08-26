from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os
import base64
import subprocess as proc

conf_path = "/etc/keyget"
flags = {"-w": "*%_@"}
if "keyget" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)

if "wireguard" not in os.listdir("/etc"):
	print("wireguard is not installed.")
	exit()
else:
	print("wireguard is installed")
	wg_dir = os.listdir("/etc/wireguard")

server = netcom.socket(ipv4, tcp)

ip = input("IP Addr: ")
port = input("Port Number: ")

ip = "localhost"
port = 12345

def main():
	while True:
		inp = input(">>> ")
		server.send(inp.encode("utf-8"))
		response = server.recv(1024).decode("utf-8")
		for key, val in flags.items():
			print(f"checking for flags.. {key}:{val}")
			if val in response:
				print(f"flag found, finding function...")
				response = response.strip(val)
				xcute = cmd.get(key)
				print(xcute)
				if xcute:
					print("executing")
					xcute(response)
					continue
		print(response)

def download(data):
	inp = input("Would you like to create a conf file?\n>>> ")
	if "n" in inp:
		return
	else:
		inp = input("Would you like to use this file with wireguard?")
		if "n" in inp:
			path = "wg0.conf"
		else:
			path = "/etc/wireguard/wg0.conf"
		with open(path, "w") as file:
			file.write(data)
		print(f"file created at: {path}")

def gen_private_key():
	key = proc.run(["wg", "genkey"], capture_output=True, text=True)

cmd = {"-w": download}
server.connect((ip, int(port)))
ack = server.recv(3).decode("utf-8")
if ack == "ack":
	server.send("ack".encode("utf-8"))
main()