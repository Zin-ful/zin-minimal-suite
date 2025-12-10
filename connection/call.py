import pyaudio
import threading as task
import time
import subprocess
import os
import socket as netcom
from socket import AF_INET as ipv4
from socket import SOCK_STREAM as tcp

"""call codes"""
codes = {"call-start": "001", "call-confirmation": "002", "call-end": "003", "call-timeout": "004", "err": "000"}

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
server_ip = input("Enter your servers IP address: ")
if not server_ip:
    server_ip = "localhost"
server_port = 10874
username = "none"
server = netcom.socket(ipv4, tcp)
incoming = False
calling = False
caller = None
conf_dict = {"user": username}
shutdown = False  # Added flag for clean shutdown

"""local conf"""
print("\n\n")
curusr = os.path.expanduser("~")
conf_path = curusr + "/.zinapp/call"
if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")
if "call" not in os.listdir(curusr + "/.zinapp"):
    os.mkdir(conf_path)
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
    global connected
    try:
        server.connect((server_ip, server_port))
        server.send("REQ".encode("utf-8"))
        reply = server.recv(3).decode("utf-8")
        if reply == "ACK":
            server.send(f"{conf_dict['user']}&{CHUNK}".encode("utf-8"))
            ack = server.recv(3).decode("utf-8")
            if ack == "ACK":
                connected = 1
                call_check_thread = task.Thread(target=listen_for_call, daemon=True)
                call_check_thread.start()
            else:
                print("No ack received, possible sync error")
                connected = 0
        else:
            connected = 0
    except Exception as e:
        print(f"Connection error: {e}")
        connected = 0

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
        device_in = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, 
                               input_device_index=int(inlist[0]), frames_per_buffer=CHUNK)
    else:
        print("no input devices found. Plug one in and retry")
        current_in = "None"
        
    if outdict:
        current_out = outdict[outlist[0]]
        device_out = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, 
                                output_device_index=int(outlist[0]), frames_per_buffer=CHUNK)
    else:
        print("no output devices found. Plug one in and retry")
        current_out = "None"
        
    init_to_server()
    return device_in, device_out, indict, outdict

def listen_for_call():
    """Fixed: Loop continuously instead of breaking after one call"""
    global incoming, caller, shutdown
    while not shutdown:
        try:
            call_attempt = server.recv(CHUNK).decode("utf-8")
            if call_attempt and ":" in call_attempt:
                code, caller = call_attempt.split(":", 1)
                if code == codes["call-start"]:
                    incoming = True
                    print(f"\nincoming call from {caller}\ntype 'attempt accept' or '88' to accept\nto decline, type 'attempt reject' or '00'\n")
                    print(f"({stat if 'stat' in globals() else 'stopped'}) >>> ", end="", flush=True)
                    # Don't break - keep listening for more calls
        except Exception as e:
            if not shutdown:
                time.sleep(0.5)

def send_to_server(data):
    try:
        if isinstance(data, str):
            server.send(data.encode("utf-8"))
        else:
            server.send(data)
    except:
        pass

def recv_from_server():
    try:
        data = server.recv(CHUNK)
        return data
    except:
        return None

def start_call():
    """Fixed: Reset caller and always ask for user input"""
    global live, calling, caller
    
    # Always ask for user when starting a new call
    to_call = input("who would you like to call? ")
    
    if not to_call:
        print("No user specified")
        return codes["call-end"]
    
    server.send(to_call.encode("utf-8"))
    live = 1
    print("sent call request, waiting for response..")
    
    try:
        confirm = server.recv(3).decode("utf-8")
        return confirm
    except:
        return codes["call-end"]

def record(audio_in):
    global live
    try:
        while live:
            audio_buffer = audio_in.read(CHUNK, exception_on_overflow=False)
            send_to_server(audio_buffer)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Record error: {e}")
    finally:
        if audio_in:
            try:
                audio_in.stop_stream()
                audio_in.close()
            except:
                pass

def playback(audio_out):
    global live_out
    try:
        while live:
            audio_buffer = recv_from_server()
            if not audio_buffer:
                time.sleep(0.01)
                continue
            audio_out.write(audio_buffer)
    except Exception as e:
        print(f"Playback error: {e}")
    finally:
        live_out = 0
        if audio_out:
            try:
                audio_out.stop_stream()
                audio_out.close()
            except:
                pass

"""main thread"""
def shell():
    global live, live_out, audio_in, audio_out, in_devices, out_devices, calling, incoming, caller, stat, shutdown
    audio_in, audio_out, in_devices, out_devices = discover()
    stat = "stopped"
    
    while True:
        inp = input(f"\n({stat}) >>> ")
        
        if incoming:
            if inp == "88" or inp == "attempt accept":
                send_to_server(codes["call-confirmation"])
                incoming = False
                calling = True
                live = 1
                live_out = 1
                stat = "running"
                
                audin_thread = task.Thread(target=record, args=(audio_in,), daemon=True)
                audout_thread = task.Thread(target=playback, args=(audio_out,), daemon=True)
                
                if audio_in:
                    try:
                        audin_thread.start()
                    except Exception as e:
                        print(f"FAILED to start input: {e}")
                        
                if audio_out:
                    try:
                        audout_thread.start()
                    except Exception as e:
                        print(f"FAILED to start output: {e}")
                
                # Reset caller after call starts
                caller = None
                continue
                
            elif inp == "00" or inp == "attempt reject":
                send_to_server(codes["call-end"])
                incoming = False
                caller = None  # Reset caller on rejection
                continue

        if "ex" in inp:
            live = 0
            shutdown = True  # Signal threads to stop
            try:
                server.close()  # Close socket connection
            except:
                pass
            print("Shutting down...")
            time.sleep(1)  # Give threads time to exit
            break
            
        elif "restart" in inp:
            live = 0
            time.sleep(0.5)
            live_out = 1
            audio_in, audio_out, in_devices, out_devices = discover()
            print("restarted. try 'start' again")
            stat = "stopped"
            caller = None  # Reset caller on restart
            
        elif "stop" in inp:
            live = 0
            stat = "stopped"
            time.sleep(0.5)
            live_out = 1
            calling = False
            caller = None  # Reset caller when stopping
            
        elif "start" in inp:
            calling = True
            live = 1
            live_out = 1
            confirm = start_call()
            
            if confirm == codes["call-confirmation"]:
                stat = "running"
                audin_thread = task.Thread(target=record, args=(audio_in,), daemon=True)
                audout_thread = task.Thread(target=playback, args=(audio_out,), daemon=True)
                
                if audio_in:
                    try:
                        audin_thread.start()
                    except Exception as e:
                        print(f"FAILED to start input: {e}")
                        
                if audio_out:
                    try:
                        audout_thread.start()
                    except Exception as e:
                        print(f"FAILED to start output: {e}")
                        
            elif confirm == codes["call-timeout"]:
                print("call timed out, user isn't available or connected to the server")
                calling = False
                caller = None  # Reset caller on timeout
                continue
            else:
                print(f"call ended or rejected")
                calling = False
                caller = None  # Reset caller on rejection/end
                
        else:
            xcute = funcs.get(inp)
            if xcute:
                cachein, cacheout = xcute()
                if cachein and cacheout:
                    audio_in = cachein
                    audio_out = cacheout

def debug():
    print("These are all your usb devices, if your mic is not found it might not be compatible\n")
    try:
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
    except:
        print("Could not run lsusb - might not be on Linux")
    return None, None

def config():
    global current_in, current_out, audio_in, audio_out
    inpset = 0
    outpset = 0
    print(f"Input device: {current_in}\nOutput device: {current_out}")
    
    if in_devices.items():
        for index, name in in_devices.items():
            print(f"INPUT {index}. {name}")
        print("Select input device (enter to skip):")
        inp = input("(config INPUT) >>> ")
        if inp:
            for index, name in in_devices.items():
                if int(inp) == int(index):
                    inpset = 1
                    inp = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, 
                                    input_device_index=int(index), frames_per_buffer=CHUNK)
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
            for index, name in out_devices.items():
                if int(outp) == int(index):
                    outpset = 1
                    outp = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, 
                                     output_device_index=int(index), frames_per_buffer=CHUNK)
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
    for key in funcs.keys():
        print(key)
    return None, None

funcs = {"help": helpy, "devices": get_dev, "set device": config, "usb": debug}

shell()
