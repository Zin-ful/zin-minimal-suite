import pyaudio
import threading as task
import time
import subprocess
import os
import socket as  netcom
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp

"""call codes"""
codes = {"call-start": "001",  "call-confirmation": "002", "call-end": "003", "call-timeout": "004", "err": "000"}

"""recording status"""
live = 1
live_out = 1

"""audio info"""

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2048
audio = pyaudio.PyAudio()

"""server info"""
connected = 0
server_ip = "127.0.0.1"
server_port = 12345
username = "none"
server = netcom.socket(ipv4, tcp)
incoming = False
calling = False
caller = None
conf_dict = {"user": username}
"""local conf"""
conf_path = "/etc/zcall"
print("\n\n")

if not "zcall" in os.listdir("/etc"):
    os.makedirs("/etc/zcall", exist_ok=True)
if "zcall.conf" not in os.listdir(conf_path):
    if conf_dict["user"] == "none":
        inp = input("It looks like this is your first time using the program\nPlease enter your desired alias: ")
        conf_dict["user"] = inp
    with open(f"{conf_path}/zcall.conf", "w") as file:
        for key, val in conf_dict.items():
            file.write(f"{key}:{val}\n")
else:
    with open(f"{conf_path}/zcall.conf", "r") as file:
        data = file.readlines()
        for item in data:
            key, val = item.split(":")
            conf_dict[key] = val.strip("\n")

"""Utility"""
def init_to_server():
    try:
        server.connect((server_ip, server_port))
        server.send("REQ".encode("utf-8"))
        reply = server.recv(3).decode("utf-8")
        if reply == "ACK":
            server.send(f"{conf_dict['user']}&{CHUNK}".encode("utf-8"))
            ack = server.recv(3).decode("utf-8")
            if ack == "ACK":
                pass
            else:
                print("No ack recieved, possible sync error")
            connected = 1
            call_check_thread = task.Thread(target=listen_for_call)
        else:
            connected = 0
    except Exception as e:
        print(e)

def discover():
    global current_in, current_out
    indict = {}
    outdict = {}
    inlist = []
    outlist = []
    device_in = None
    device_out = None
    for i in range(audio.get_device_count()):
        device = audio.get_device_info_by_index(i)
        if device['maxInputChannels'] > 0:
            indict.update({str(i): device['name']})
            inlist.append(str(i))
        if device['maxOutputChannels'] > 0:
            outdict.update({str(i): device['name']})
            outlist.append(str(i))

    if indict:
        current_in = indict[inlist[0]]
        device_in = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=int(inlist[0]), frames_per_buffer=CHUNK)
    else:
        print("no input devices found. Plug one in and retry")
        current_in = "None"
    if outdict:
        current_out = outdict[outlist[0]]
        device_out = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index=int(outlist[0]), frames_per_buffer=CHUNK)
    else:
        print("no output devices found. Plug one in and retry")
        current_in = "None"
    init_to_server()
    return device_in, device_out, indict, outdict

def listen_for_call():
    global incoming, caller
    while not calling:
        call_attempt = server.recv(CHUNK)
        if call_attempt:
            code, caller = call_attempt.split(":")
        if code == codes["call-start"]:
            break
    incoming = True
    print(f"incoming call from {caller}\ntype 'attempt accept' or '88' to accept\nto decline, type 'attempt reject' or '00'\n\n")

def send_to_server(data):
    try:
        server.send(data.encode("utf-8"))
    except:
        pass

def recv_from_server():
    data = server.recv(CHUNK)
    if data:
        return data
def start_call():
    global live
    if not caller:
        to_call = input("who would you like to call?")
    else:
        to_call = caller
    server.send(to_call.encode("utf-8"))
    live = 1
    print("sent call request, waiting for response..")
    confirm = server.recv(3)
    confirm = confirm.decode("utf-8")
    return confirm

def record(audio_in):
    global live
    try:
        while live:
            audio_buffer = audio_in.read(CHUNK, exception_on_overflow=False)
            send_to_server(audio_buffer)
        if not live:
            print("stopping")
            audio_in.stop_stream()
            audio_in.close()
            live = 0
            while live_out:
                time.sleep(0.01)
            audio_out.stop_stream()
            audio_out.close()
            audio.terminate()
    except KeyboardInterrupt:
        print("stopping")
        audio_in.stop_stream()
        audio_in.close()
        live = 0
        while live_out:
            time.sleep(0.01)
        audio_out.stop_stream()
        audio_out.close()
        audio.terminate()

def playback(audio_out):
    global live_out
    audio_buffer = None
    while live:
        audio_buffer = recv_from_server()
        if not audio_buffer:
            print("No data from server")
            time.sleep(0.1)
            continue
        audio_out.write(audio_buffer)
    live_out = 0


"""main thread"""

def shell():
    global live, audio_in, audio_out, in_devices, out_devices, calling
    audio_in, audio_out, in_devices, out_devices = discover()
    stat = "stopped"
    while True:
        inp = input(f"\n({stat}) >>> ")
        if incoming:
            if inp == "88" or inp == "attempt accept":
                send_to_server(codes["call-confirmation"])
            elif inp == "88" or inp == "attempt accept":
                send_to_server(codes["call-end"])
            inp = "start"

        if "ex" in inp:
            live = 0
            break
        elif "restart" in inp:
            audio_in, audio_out, in_devices, out_devices = discover()
            print("restarted. try 'start' again")
            live = 0
            stat = "stopped"
        elif "stop" in inp:
            live = 0
            stat = "stopped"
        elif "start" in inp:
            calling = True
            confirm = start_call()
            if confirm == codes["call-confirmation"]:
                pass
            elif confirm == codes["call-timeout"]:
                print("call timed out, user isnt available or connected to the server")
                continue

            stat = "running"
            audin_thread = task.Thread(target=record, args=(audio_in,))
            audout_thread = task.Thread(target=playback, args=(audio_out,))
            if in_devices or audio_in:
                try:
                    audin_thread.start()
                except Exception as e:
                    print(f"FAILED: {e}")

            if out_devices or audio_out:
                try:
                    audout_thread.start()
                except Exception as e:
                    print(f"FAILED: {e}")
        else:
            xcute = funcs.get(inp)
            if xcute:
                cachein, cacheout = xcute()
                if cachein and cacheout:
                    audio_in = cachein
                    audio_out = cacheout

def debug():
    print("These are all your usb devices, if your mic is not found it might not be compatable with your hardware\nor operating system (usually an issue with audio interfaces like Focusrite or Presonus)\n")
    usbs = []
    usbdevs = str(subprocess.run("lsusb", capture_output=True, text=True))
    trash, usbdevs = usbdevs.split("stdout='")
    usbdevs, trash = usbdevs.split("stderr")
    while "\n" in usbdevs:
        dev, usbdevs = usbdevs.split("\n", 1)
        usbs.append(dev)
    usbs.append(usbdevs)
    for item in usbs:
        print(item)
    return None, None

def config():
    global current_in, current_out
    inpset = 0
    outpset = 0
    print(f"Input device: {current_in}\nOutput device: {current_out}")
    if in_devices.items():
        for index, name in in_devices.items():
            print(f"INPUT {index}. {name}")
        print("Select input device (enter to skip):")
        inp = input("(config INPUT) >>> ")
        if inp:
            for index, nane in in_devices.items():
                if int(inp) == int(index):
                    inpset = 1
                    inp = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=int(index), frames_per_buffer=CHUNK)
                    current_in = in_devices[index]
                    print(f"INPUT changed to {in_devices[index]}")
                    break
    else:
        print("No input devices to choose, moving to output")

    if out_devices.items():
        for index, name in out_devices.items():
            print(f"OUTPUT {index}. {name}")
        print("Select output device (enter to skip):")
        outp = input("(config OUTPUT) >>> ")
        if outp:
            for index, nane in out_devices.items():
                if int(outp) == int(index):
                    outpset = 1
                    outp = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index=int(index), frames_per_buffer=CHUNK)
                    current_out = out_devices[index]
                    print(f"OUTPUT changed to {out_devices[index]}")
                    break
    else:
        print("No output devices to choose, finalizing")
    if not inpset:
        inp = audio_in
    if not outpset:
        outp = audio_out
    return inp, outp

def get_dev():
    print(f"\ncurrent input: {current_in}\ncurrent_output: {current_out}\n")

    if in_devices.items():
        for index, name in in_devices.items():
            print(name, "<<< input")
    else:
        print("No input devices found. Use 'restart' to rescan")

    if out_devices.items():
        for index, name in out_devices.items():
            print(name, "<<< output")
    else:
        print("No output devices found. Use 'restart' to rescan")
    return None, None

def helpy():
    for key, val in funcs.items():
        print(key)
    return None, None

funcs = {"help": helpy, "devices": get_dev, "set device": config, "usb": debug}



shell()


