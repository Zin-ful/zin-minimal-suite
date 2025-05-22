import subprocess as proc
import time

def locateall(ip, subnet, speed, wait):
		print(f"Please be patient, this will take {float(wait) * 255} or maybe {float(speed) * 255} seconds.")
		time.sleep(2)
		ips = []
		oct1, oct2, oct3, oct4 = ip.split(".")
		i = 1
		while i < 254:
			try:
				output = proc.check_output(["ping", "-c 1", f"-i {speed}", f"-W {wait}", f"{oct1}.{oct2}.{oct3}.{i}"], text=True)
			except:
				output = "nope"
			if "bytes from" in output:
				print(f"Device found on: {oct1}.{oct2}.{oct3}.{i}, adding to report")
				ips.append(f"{oct1}.{oct2}.{oct3}.{i}")
			else:
				print(f"no device found on: {oct1}.{oct2}.{oct3}.{i}")
			i += 1
		for item in ips:
			print(f"##FOUND: {item}##")

def target(ip, subnet, speed, wait):
	return
	
def locatesubs(ip, subnet, wait):
	return
cmds = {"sweep": locateall, "megasweep": locatesubs, "target": target,}

while True:
	print("commands:\ntarget (ip)\nsweep (ip)\nmegasweep (ip) -start (starting subnet)")
	print("if you want to put options:\n-start\n-speed\n-wait")
	speed = ''
	wait = ''
	subnet = ''
	inp = input(">>> ")
	if "exit" in inp:
		exit()
	if " " in inp:
		cmd, ip = inp.split(" ", 1)
		ip = ip.strip()
	if "-start" in ip:
		ip, subnet = ip.split(" -start ")
		if " " in subnet:
			subnet, cache = subnet.split(" ", 1)
			ip = ip + " " + cache
	if "-speed" in ip:
		ip, speed = ip.split(" -speed ")
		print(ip, speed)
		if " " in speed:
			speed, cache = speed.split(" ", 1)
			ip = ip + " " + cache
	if "-wait" in ip:
		ip, wait = ip.split(" -wait ")
		print(ip, wait)
		if " " in wait:
			wait, cache = wait.split(" ", 1)
			ip = ip + " " + cache
	ip = ip.strip()
	if not speed or '' in speed or speed == " ":
		speed = "0.1"
	if not wait or '' in wait or wait == " ":
		wait = "0.02"
	if float(speed) < 0.1:
		speed = "0.1"
	if float(wait) < 0.02:
		wait = "0.02"
	print(f"probing {ip}, options: speed={speed} wait={wait} subnet={subnet}")
	time.sleep(1)
	xcute = cmds.get(cmd)
	if xcute:
		xcute(ip, subnet, speed, wait)
	else:
		print("Sorry thats not a command.")
