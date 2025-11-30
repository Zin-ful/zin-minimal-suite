from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp
import socket as netcom
import os

curusr = os.path.expanduser("~")

conf_path = curusr+"/.zinapp/keyget"
flags = {"-w": "*%_@"}

if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "keyget" not in os.listdir(curusr+"/.zinapp"):
	os.mkdir(conf_path)

if "wireguard" not in os.listdir("/etc"):
	print("wireguard is not installed.")
	exit()
else:
	print("wireguard is installed")

server = netcom.socket(ipv4, tcp)
ip = input("IP Addr: ")
if not ip:
	ip = "localhost"
port = 10592
def main():
	while True:
		executed = 0
		inp = input(">>> ")
		if "ex" in inp:
			exit()
		server.send(inp.encode("utf-8"))
		response = server.recv(4196).decode("utf-8")
		for key, val in flags.items():
			if val in response:
				response = response.strip(val)
				xcute = cmd.get(key)
				if xcute:
					xcute(response)
					executed = 1
		if not executed:
			print(response)

def download(data):
	keys, data = data.split(":", 1)
	inp = input("Would you like to create a local configuration  file? (yes will continue to creation options)\n>>> ")

	if "n" in inp:
		return
	inp = input("Would you like write this file to /etc/wireguard? (no will save it to your running directory)\n>>>")
	if "n" in inp:
		path = ""
	else:
		path = "/etc/wireguard/"
	with open(path+"wg0.conf", "w") as file:
		file.write(data)

	cache, keys = keys.split("=", 1)
	pubkey, privkey = keys.split("&")
	

	with open(path+"public.key", "w") as file:
		file.write(pubkey)
	cache, pubkey = pubkey.split("=", 1)
	with open(path+"private.key", "w") as file:
		file.write(privkey)
		print(f"file created at: {path}wg0.conf\npubkey created at {path}public.key\nprivkey created at {path}private.key")

def search():
    return

cmd = {"-w": download, "-s": search}
server.connect((ip, int(port)))
ack = server.recv(3).decode("utf-8")
if ack == "ack":
	server.send("ack".encode("utf-8"))
main()
