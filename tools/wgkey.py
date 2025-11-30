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
	    elif "auto" in inp:
	        auto_start()
	        continue
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

def auto_start():
    inp = input("**Press enter to return**\n\nSelect daemon type for autostart\n1. Systemd\n2. Runit\n\n>>>")
    if not inp:
        return
    if "1" in inp:
        print("Wireguard on Systemd installations usually already creates a service for itself. Verify the service doesnt exist at:\n/etc/systemd/system/\nbefore continuing")
        inp = input("Continue?")
        if "y" not in inp:
            return
        with open("/etc/systemd/system/wg-quick@.service", "w") as file:
            file.write("[Unit]\nDescription=WireGuard via wg-quick(8) for %I\nAfter=network.target\nDocumentation=man:wg-quick(8)\nDocumentation=man:wg(8)\nDocumentation=https://www.wireguard.com/\nDocumentation=https://www.wireguard.com/quickstart/\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/usr/bin/wg-quick up %i\nExecStop=/usr/bin/wg-quick down %i\nExecReload=/usr/bin/wg-quick down %i ; /usr/bin/wg-quick up %i\nEnvironment=WG_ENDPOINT_RESOLUTION_RETRIES=infinity\n[Install]\nWantedBy=multi-user.target")    
        print("wg-quick@.service written. if needed, run 'systemctl daemon-reload' and 'systemctl enable wg-quick@wg0.service'")
    elif "2" in inp:
        start_path = "/etc/runit/runsvdir/default/wg"
        os.makedirs(start_path, exist_ok=True)
        print("writing run")
        with open(start_path+"/run", "w") as file:
            file.write("#!/bin/sh\necho 'RUN: attempting wireguard start' > /dev/kmsg\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nexport PATH\nexec 2>&1\nWG_CONF='/etc/wireguard/wg0.conf'\nsleep 5\nif [ -f $WG_CONF ]; then\n    echo 'RUN: Starting wg0...' > /dev/kmsg\n    wg-quick up $WG_CONF\nelse\n    echo 'RUN: wireguard config not found' > /dev/kmsg\n    exit 1\nfi\necho 'RUN: wireguard brought up successfully' > /dev/kmsg\nexec tail -f /dev/null")
        print("writing finish")
        with open(start_path+"/finish", "w") as file:
            file.write("#!/bin/sh\necho 'RUN: attempting to bring wireguard down' > /dev/kmsg\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nexport PATH\nexec 2>&1\nWG_CONF='/etc/wireguard/wg0.conf'\nif [ -f $WG_CONF ]; then\n    echo 'RUN: Bringing down wg0...' > /dev/kmsg\n    wg-quick down $WG_CONF\nelse\n    echo 'RUN: WireGuard config not found at $WG_CONF' > /dev/kmsg\nfi\nexit 1")
        print("marking both as executable")
        os.chmod(start_path+"/run", 0o755)
        os.chmod(start_path+"/finish", 0o755)
        print("run and finish file created, if needed, run 'sudo sv enable wg' to enable at start")
    else:
        return

def download(data):
	keys, data = data.split(":", 1)
	inp = input("1. Dont save configuration file\n2. Save configuration file to current directory\n3. Save configuration file to /etc/wireguard\n\n>>>")
    if "1" in inp:
        print(data)
	elif "2" in inp:
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
