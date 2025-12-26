import os
import threading as task
from time import sleep
curusr = os.path.expanduser("~")

path = input("Input the path to the file you want analyzed\n\n>>> ")
if path[0] != "/":
	path = curusr+"/"+path

unique_lines = []

omitted = []

included = []

done = []

while True:
	inp = input("Enter any phrases you want sorted out of the result (any item having an inputted phrase will be removed)\n\n(Press enter to break) >>> ")
	if inp:
		omitted.append(inp)
	else:
		break

while True:
	inp = input("Enter any phrases you want included in the result (any item not having an inputted phrase will be removed)\n\n(Press enter to break) >>> ")
	if inp:
		included.append(inp)
	else:
		break

print("querying cpu")
cpus = os.cpu_count()
print(f"total threads = {cpus}")

def get_len():
	with open(path, "r") as file:
		length = len(file.readlines())
	return length
	
def get_range():
	print("getting range")
	total = get_len()
	part_size = total // cpus
	remainder = total % cpus
	print(f"parts size = {part_size}")
	ranges = []
	start = 0
	
	for i in range(cpus):
		end = start + part_size + (1 if i < remainder else 0)
		ranges.append((start, min(end, total)))
		start = end
	return ranges
	
def read_range(id, supplied_range):
	print(f"{id}: reading file")
	with open(path, "r") as file:
		all = file.readlines()
	print(f"{id}: splitting range start - end")
	num1, num2 = supplied_range
	read_list = []
	i = 0
	print(f"{id}: creating new list")
	for i in range(num1, num2):
		read_list.append(all[i])
		i += 1
	print(f"{id}: deleting old list")
	del all
	print(f"{id}: finding unique lines")
	read_len = len(read_list)
	step = max(1, read_len // 2)
	for i, item in enumerate(read_list, 1):
		if item not in unique_lines:
			unique_lines.append(item)
		if i % step == 0 or i == read_len:
			percent = (i * 100) // read_len
			percent -= percent % 5
			print(f"{id}: {percent}% read")
	done.append("done")

def whitelist():
	global unique_lines
	print(f"reading unique list")
	sleep(0.1)
	print("removing all lines that are not in the included phrases")
	unique_lines = [item for item in unqiue_lines if any(phrase in item for phrase in included)]

def blacklist():
	global unique_lines
	print(f"reading unique list")
	sleep(0.1)
	print("removing lines with omitted phrases")
	unique_lines = [item for item in unqiue_lines if not any(phrase in item for phrase in omitted)]

print("getting file length")
length = get_len()
print(length)
ranges = get_range()

if length > 10000:
	i = 0
	is_threaded = 1
	for i in range(cpus):
		thread = task.Thread(target=read_range, args=(f"Thread-{i}", ranges[i]))
		thread.start()
else:
	is_threaded = 0
	read_range("Thread-Main", (0, length - 1))

if included:
	whitelist()
if omitted:
	blacklist()

print("searching finished")
print(f"length of original text: {length}\nlength of new text: {len(unique_lines)}")
print("writing to file 'results.txt'")
while len(done) != 4 and is_threaded:
	sleep(2)
print("Press enter to continue")
inp = input()
with open("results.txt", "w") as file:
	for item in unique_lines:
		file.write(f"{item}\n")

print("data written, printing results")

for item in unique_lines:
	print(item)
	sleep(0.01)