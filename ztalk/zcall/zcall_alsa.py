import pyaudio
import threading
import time

live = 1
live_out = 1

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

audio = pyaudio.PyAudio()
print("\n\n\n\n\n")

audio_buffer = None


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
		print(f"{i}: {device['name']}:\nInput channels - {device['maxInputChannels']}\nOutput channels - {device['maxOutputChannels']}")
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
	if outdict:
		current_out = outdict[outlist[0]]
		device_out = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output_device_index=int(outlist[0]), frames_per_buffer=CHUNK)
	else:
		print("no output devices found. Plug one in and retry")
	
	return device_in, device_out, indict, outdict

def shell():
	global live, audio_in, audio_out
	while True:
		inp = input("\n>>> ")
		print("\n")
		if "stop" in inp or "ex" in inp:
			live = 0
			break
		if "start" in inp:
			audio_in, audio_out, in_devices, out_devices = discover()
			audin_thread = threading.Thread(target=record, args=(audio_in,))
			audout_thread = threading.Thread(target=playback, args=(audio_out,))
			if in_devices or audio_in:
				try:
					audin_thread.start()
				except Exception as e:
					print(f"FAILED: {e}")
			"""if out_devices or audio_out:
				try:
					audout_thread.start()
				except Exception as e:
					print(f"FAILED: {e}")"""
			
def config(flow):
	return device_in, device_out

def get_dev():
	for index, name in in_devices.items():
		print(name, "<<< input")
	for index, name in out_devices.items():
		print(name, "<<< output")
	print(f"\ncurrent input: {current_in}\ncurrent_output: {current_out}")

funcs = {"devices": get_dev, "set device": config}

def record(audio_in):
	global live, audio_buffer
	try:
		while live:
			audio_buffer = audio_in.read(CHUNK)
			print(len(audio_buffer))
		if not live:
			print("stopping")
			audio_in.stop_stream()
			audio_in.close()
			live = 0
			while live_out:
				time.sleep(0.01)
			audio_out.stop_stream()
			audio_out.close()
			audout_thread.join()
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
		audout_thread.join()
		audio.terminate()
		
def playback(audio_out):
	global live_out
	while live:
		time.sleep(0.01)
		audio_out.write(b"\x00" * RATE)
#audio_out.write(audio_buffer)
	live_out = 0


shell()

