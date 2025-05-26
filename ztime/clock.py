import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import time
import datetime
import random
conf_path = "/etc/ztime"
screens = {}
colors = {}
offset = 1
done = 0
pos = 0
highlight = "0"
timecolor = "0"
morningmsg = "0"
noonmsg = "0"
afternoonmsg = "0"
eveningmsg = "0"
nightmsg = "0"
msgs = {"morning": morningmsg, "noon": noonmsg, "afternoon": afternoonmsg, "evening": eveningmsg, "night": nightmsg}
mornings = ["Goodmorning! Time to get up!", "Remember to eat breakfast or grab a snack!", "Have a good day today!", "Is it winter yet?", "Another day another.. day?", "I DONT KNOWWW I DONT KNOWW I DONT KN00W I DONT KN00W", "LETS GET THIS BBAAAAAAAAAAAGGGGGGG", "Depending on the time of year your either real mad or mildly expectant", "What time is it? TIME FOR YOU TO GET A WATCH AAAAHHHH"]
noons = ["ITS LUNCH TIME FUCKER", "Remember to grab some food!", "Its noon, are you even awake yet?", "KAMEHAMEHAAAAAAAA ELEGANT BLASTAAAHH", "Wakey wakey eggs and bakey, cause your ass aint up yet.", "FIVE NIGHTS AT FREDDIESSSSSSS IS THAT WHERE YOU WANNA BE?", "YOU JUST DONT GET ITTTTTT WHY WOULD YOU WANT TO STAY?", "NA NA NANANA NA NA THEN I POPPED OFF", "Oh brother THIS GUY STINKS"]
afternoons = ["Dinner should be ready in a few hours", "This would be a good time for [insert activity]", "Do you know how long it took to write all these? Dont look at the code.", "SSSSUUUUUUUPPPPPPERRRR SAAAAAIIIYAN THREEEEEEEEEEEEEEEEE", "Dubstep is unironically pretty good", "Fun fact, hahaha", "Grab lunch if you forgot!", "Watching fnaf, ill update this later", "If this crashes itll be SOO FUMNNY CANT WAIT TO FIX IT", "NIGHTMARE NIGHTMARE NIGHTMARE"]
evenings = ["Oh its minecraft time", "TIME FOR THE CRAFT", "Top 3 movies: Iron giant, Wild Robot, Interstellar", "You better have ate dinner bruh", "Boy its gettin that time of day aint it?", "Im running out of ideas here man", "You should look into grilled cheeses. Make them with butter, not the fake stuff", "OH GOD THEIR IN THE TREES JESUS CHRI"]
nights = ["jiiiiiglyy puuuufff jiggillyyyy puffff", "Everyones asleep? Would be a great time to record at full volume", "It would probably be a good time to sleep.", "If your clock isnt accurate these messages might not make sense.", "sleeep sleeeeeeeep SLEEEEEEP FUCK DAMNIT SLEEEP GODD CHRIST", "hey.. THEY HIT THE PENTAGON OH GOD NO NOT THE PENTAGON", "How fucked is your sleep schedule man?", "i bet you forgot something today didnt you"]
bar = ""

if "ztime" not in os.listdir("/etc"):
	os.makedirs(conf_path, exist_ok=True)

if "clock.conf" not in os.listdir(conf_path):
	with open(f"{conf_path}/clock.conf", "w") as file:
		for times, msg in msgs.items():
		    file.write(f"{times}={msg}\n")
else:
    with open(f"{conf_path}/clock.conf", "r") as file:
        stuff = file.readlines()
        for item in stuff:
            times, msg = item.split("=")
            msgs[times] = msg

def main(stdscr):
    global screens, height, width, highlight, timecolor, daycolor, bar
    height, width = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    timecolor = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    daycolor = curses.color_pair(3)
    stdscr.clear()
    stdscr.refresh()
    main_win = curses.newwin(height - 5, width, 2, 0)
    main_win.clear()
    main_win.refresh()
    screens.update({"source": stdscr})
    screens.update({"main": main_win})
    i = 0
    while i < width:
        bar += " "
        i += 1
    clock = task.Thread(target=update, args=[screens,])
    clock.start()
def update(screens):
    morning = False
    noon = False
    afternoon = False
    evening = False
    night = False
    while True:
        if not done:
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            year, month, day = now.split("-")
            day, times = day.split(" ")
            hour, mins, secs = times.split(":")
            if int(hour) <= 12 and int(hour) > 4:
                morning = True
                noon = False
                afternoon = False
                evening = False
                night = False
            elif int(hour) > 12 and int(hour) < 14:
                morning = False
                noon = True
                afternoon = False
                evening = False
                night = False
            elif int(hour) >= 14 and int(hour) < 18:
                morning = False
                noon = False
                afternoon = True
                evening = False
                night = False
            elif int(hour) >= 18 and int(hour) < 22:
                morning = False
                noon = False
                afternoon = False
                evening = True
                night = False
            elif int(hour) >= 22:
                noon = False
                morning = False
                afternoon = False
                evening = False
                night = True
            phrase = "YEAR"
            screens["main"].addstr(2, width // 2 - (len(phrase) // 2), phrase, daycolor)
            screens["main"].addstr(4, width // 2 - (len(year) // 2), year, timecolor)
            phrase = "MNTH"
            screens["main"].addstr(6, width // 2 - (len(phrase) // 2), phrase, daycolor)
            screens["main"].addstr(8, width // 2 - (len(month) // 2), month, timecolor)
            phrase = "DATE"
            screens["main"].addstr(10, width // 2 - (len(phrase) // 2), phrase, daycolor)
            screens["main"].addstr(12, width // 2 - (len(day) // 2), day, timecolor)
            screens["main"].addstr(14, width // 2 - (len(f"{hour} HOURS {mins} MINUTES {secs} SECONDS") // 2), f"{hour} HOURS {mins} MINUTES {secs} SECONDS", timecolor)
            screens["main"].addstr(18, width // 2 - (len(now) // 2), now, daycolor)
            if msgs["morning"].strip() == "0":
                msgs["morning"] = mornings[random.randint(0, len(mornings) - 1)]
            elif msgs["noon"].strip() == "0":
                msgs["noon"] = noons[random.randint(0, len(noons) - 1)]
            elif msgs["afternoon"].strip() == "0":
                msgs["afternoon"] = afternoons[random.randint(0, len(afternoons) - 1)]
            elif msgs["evening"].strip() == "0":
                msgs["evening"] = evenings[random.randint(0, len(evenings) - 1)]
            elif msgs["night"].strip() == "0":
                msgs["night"] = nights[random.randint(0, len(nights) - 1)]
                
            if morning:
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["morning"]) // 2), msgs["morning"], daycolor)
            elif noon:
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["noon"]) // 2), msgs["noon"], daycolor)
            elif afternoon:
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["afternoon"]) // 2), msgs["afternoon"], daycolor)
            elif evening:
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["evening"]) // 2), msgs["evening"], daycolor)
            elif night:
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["night"]) // 2), msgs["night"], daycolor)
            screens["main"].refresh()
            time.sleep(0.3)
            if int(hour) == 23 and int(mins) == 59 and int(secs) == 59:
                with open(f"{conf_path}/clock.conf", "r") as file:
                    stuff = file.readlines()
                    for item in stuff:
                        times, msg = item.split("=")
                        msgs[times] = msg
                time.sleep(0.5)

def select(key, screens):
    global pos
    if key == ord("s"):
        pos += 1
        if pos >= len(applist):
            pos = len(applist) - 1
        back = 1
    elif key == ord("w"):
        pos -= 1
        if pos <= 0:
            pos = 0
        back = -1
    screens["main"].addstr(pos + offset - back, 0, applist[pos - back])
    screens["main"].addstr(pos + offset, 0, applist[pos], highlight)

wrapper(main)
