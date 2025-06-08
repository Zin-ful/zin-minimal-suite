import sounddevice as sd
import threading
import time


channels = 1
rate = 44100
chunk = 4096
durate = 0.1

audio_buffer = None

def shell():
	global live
	while True:
		inp = input(">>> ")
		if "stop" in inp or "ex" in inp:
			live = 0
			break


def record():
	audrec = sd.rec(int(durate * rate),
		samplerate=rate,
		channels=channels,
		dtype='float32'
	)
	sd.wait()
	playback(audrec)
	
def playback(aud):
	sd.play(aud, samplerate=rate)
	sd.wait()


audin_thread = threading.Thread(target=record)
#audout_thread = threading.Thread(target=playback)

audin_thread.start()
#audout_thread.start()

shell()

