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

audio_in = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

audio_out = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

audio_buffer = None

def shell():
	global live
	while True:
		inp = input(">>> ")
		if "stop" in inp or "ex" in inp:
			live = 0
			break


def record():
	global live, audio_buffer
	try:
		while live:
			audio_buffer = audio_in.read(CHUNK)
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
		
def playback():
	global live_out
	while live:
		time.sleep(0.01)
		audio_out.write(b"\x00" * RATE)
#audio_out.write(audio_buffer)
	live_out = 0


audin_thread = threading.Thread(target=record)
audout_thread = threading.Thread(target=playback)

#audin_thread.start()
#audout_thread.start()

shell()

