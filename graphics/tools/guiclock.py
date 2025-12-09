#!/usr/bin/env python3
import os
import threading as task
import time
import curses
from curses import wrapper
from curses.textpad import Textbox
import time
import datetime
import random
curusr = os.path.expanduser("~")
conf_path = curusr+"/.zinapp/ztime"
screens = {}
colors = {}
offset = 1
done = 0
globalpos = 0
pause = 0
highlight = "0"
timecolor = "0"
morningmsg = "0"
noonmsg = "0"
afternoonmsg = "0"
eveningmsg = "0"
nightmsg = "0"
current_message = "none"

msgs = {"morning": morningmsg, "noon": noonmsg, "afternoon": afternoonmsg, "evening": eveningmsg, "night": nightmsg}

mornings = ["Goodmorning! Time to get up!", "Remember to eat breakfast or grab a snack!", "Have a good day today!", "Is it winter yet?", "Another day another.. day?", "I DONT KNOWWW I DONT KNOWW I DONT KN00W I DONT KN00W", "LETS GET THIS BBAAAAAAAAAAAGGGGGGG", "Depending on the time of year your either real mad or mildly expectant", "What time is it? TIME FOR YOU TO GET A WATCH AAAAHHHH", "hm? oh im just watching a video on can openers", "oh. my. god. i cannot believe he was gay", "i miss facebook marketplace",
           "how many computers are we at? lets talk about this never.", "PUNCH ME IN MY PERFECT JAWLINE", "MY BAETEEN", "kick rocks kid", "QUACK", "mr sandman, bring me a dream", "I DIDNT ASK TO BE BORN DADS", "4th RULE OF POPOS TRAINING", "what is he?", "all these squares make a circle", "bop bop bop", "SHAPE OF AN L ON HER FOREHEAD", "team three star?", "oooh we got cancles brewing", "all i wanna be is a dad who gets to see a super sayian", "f*ck it were aborting cell", "NEEERRRRDDD", "did our heart just skip a beat?", "that is so precious", "nana nana na na JENNAY", "OLIVIA OLIVIA WHAAA AAHH", "divorce HEHEHEHHHE", "'you know what you wanna do today?' nah.", "bro go eat some FUCKING oatmeal", "theres 23 walking goldfish from terraria walking thro-", "divorce HUUHQUAHA"]

noons = ["ITS LUNCH TIME FUCKER", "Remember to grab some food!", "Its noon, are you even awake yet?", "KAMEHAMEHAAAAAAAA ELEGANT BLASTAAAHH", "Wakey wakey eggs and bakey, cause your ass aint up yet.", "FIVE NIGHTS AT FREDDIESSSSSSS IS THAT WHERE YOU WANNA BE?", "YOU JUST DONT GET ITTTTTT WHY WOULD YOU WANT TO STAY?", "NA NA NANANA NA NA THEN I POPPED OFF", "Oh brother THIS GUY STINKS", "damn gammies going super saiyan", "crawling around on all fours like a goblin",
        "nail, kick this guys ass","they wont be able to air it on tv cause it will be SO BRUTAL","my stupid fuckin headphone died","how manu computers do you have now?","windows blows. call it blowthose. HA", "we shall be like the birds and the bees. Ha, no robo", "yes this time has the most dbz references, i was tired", "so... *lip smack*, come here often?", "Oh look what time it is! what? i cant read.", "i gave you a rhetorical answer!", "if you learned how to code you could probably improve this", "is that seth rogan?", "momster lebgens", "C-A-M-P-F-I-R-E S-O-N-G SONG", "omfg clash royal doesnt work on my phone", "double entandra double entandra", "hmm... divore HEHUUUUULALAL"]

afternoons = ["Dinner should be ready in a few hours", "This would be a good time for [insert activity]", "Do you know how long it took to write all these? Dont look at the code.", "SSSSUUUUUUUPPPPPPERRRR SAAAAAIIIYAN THREEEEEEEEEEEEEEEEE", "Dubstep is unironically pretty good", "Fun fact, hahaha", "Grab lunch if you forgot!", "Watching fnaf, ill update this later", "If this crashes itll be SOO FUMNNY CANT WAIT TO FIX IT", "NIGHTMARE NIGHTMARE NIGHTMARE",
             "how do you spell that?", "SAME SHIT. SAME SHIT DIFFERENT DAY", "wtf did this dog just say?", "i gotta remove creepers bruh", "ONE MORE ARROW. ONE. MORE.", "who tf is lickin their balls back there", "I BREAAK WHEN YOU CALL MEEEEE", "SCARED OF LEAVINGGGING", "WHEN YOUR NOT TALKING TO ME", "your music SUCKS", "oh shit papa meat released a new vid", "I AM THE KING. AT FIVE NIGHTS AT FREDDYSYSS", "tf am i hearing?", "good job super star", "'washer song'", "NAAAIILL. CLEAN MY JOWELS", "did i just get hit by a midget with a bowl cut?", "freaky alien genotype", "this mfs head is made out of playdough", "your face looks like a busted can of biscuts", "PIZZA H U u t PIZZA HUT", "fair point, divorce HAAMHAMAHmAHMAH", "lets UP THOSE NUMBERSSSS", "your family is looking for you.."]

evenings = ["Oh its minecraft time", "TIME FOR THE CRAFT", "Top 3 movies: Iron giant, Wild Robot, Interstellar", "You better have ate dinner bruh", "Boy its gettin that time of day aint it?", "Im running out of ideas here man", "You should look into grilled cheeses. Make them with butter, not the fake stuff", "OH GOD THEIR IN THE TREES JESUS CHRI", "poppin pillies i feel just like a rock starrrr", "damn look at that dudes TIDDIES", "DENDE. MY NAME IS DENDE. SAY IT", "GREGORY",
           "WHIIIIITEEE ELEVATOR", "I GOT HIT ALL UP IN MY SHNOZZZ", "IVE HAD ENOUGH OF THIS, GONNA SAY WHAT I WAAAA", "This mf has to pay for her groceries", "Ughn Ughn UGHN", "damn my back itches", "gotta get rations or else i wont eat tonight", "yaEH", "wtf typa ass music is this", "TWO. TWO SENTENCES OR LESS", "call me superkameguru", "MY BABY BOYY", "all youll be feeling is OBLIVION", "hey mr P, whip me up some new threads", "I AM A SUPER SANDWICH", "yur", "your headphones SUCK", "this has to be some of the worst music ive ever heard", "that dog you left in minecraft is waiting for you to come back", "'oAt MeAl HaS nO nUtRiTiOn'", "BALD > BALD > BALD >", "EGG - EGG SANDWICH", "PIZZA H U u divorce HAAHPIHAPHGPE", "which phone did you text me on"]

nights = ["jiiiiiglyy puuuufff jiggillyyyy puffff", "Everyones asleep? Would be a great time to record at full volume", "It would probably be a good time to sleep.", "If your clock isnt accurate these messages might not make sense.", "sleeep sleeeeeeeep SLEEEEEEP FUCK DAMNIT SLEEEP GODD CHRIST", "hey.. THEY HIT THE PENTAGON OH GOD NO NOT THE PENTAGON", "How fucked is your sleep schedule man?", "i bet you forgot something today didnt you",
         "check siggy", "kicking this mf in the BALLs", "i hate this fat bald bitch you dont know shit", "im up late? nigga these candles arent gonna pour themselves", "i made 80 bucks :D", "'on fucking GOD i did'", "up late i see, possibly, dragon ball?", "BULMA SEX MAKES BABIES", "i wonder if they ever finished watching fnaf", "so. figured out what you wanna do yet?", "hmm. hmm. neat.", "senzu bean!", "hey krillin, 'senzu bean'", "im pissed i cant finish this day in my mobile game", "tell that bitch NOOOAAHH to make me a samwich", "imma plant me a dumbass tree", "500 MESSAGES????", "cha la inch chala", "HAM SANDWICH", "MOUTH", "ah fack i lost my other phone", "i kknnnow your hiding"]

bar = ""

msg_list = []

all_messages = {}
all_times = [mornings, noons, afternoons, evenings, nights]

for unit in all_times:
    for item in unit:
        all_messages.update({item: "false"})



if ".zinapp" not in os.listdir(curusr):
    os.mkdir(curusr+"/.zinapp")

if "ztime" not in os.listdir(curusr+"/.zinapp"):
    os.mkdir(conf_path)

if "ach.conf" not in os.listdir(conf_path):
    with open(f"{conf_path}/ach.conf", "w") as file:
        for times, state in all_messages.items():
            file.write(f"{times}={state}\n")
else:
    with open(f"{conf_path}/ach.conf", "r") as file:
        stuff = file.readlines()
        for item in stuff:
            times, state = item.split("=")
            all_messages[times.strip()] = state.strip()


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

def save(line):
    if not line:
        return
    all_messages[line] = "true"
    with open(f"{conf_path}/ach.conf", "w") as file:
        for times, state in all_messages.items():
            file.write(f"{times}={state}\n")

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
    main_win = curses.newwin(height - 1, width, 2, 0)
    main_win.clear()
    main_win.refresh()
    screens.update({"source": stdscr})
    screens.update({"main": main_win})
    i = 0
    while i < width:
        bar += " "
        i += 1
    clock = task.Thread(target=update, args=[0])
    clock.start()
    inps(screens, clock)

def update(temp):
    global current_message
    if temp:
        screens["main"].addstr(22, 0, bar, daycolor)
        screens["main"].addstr(22, width // 2 - (len(current_message) // 2), current_message, daycolor)
        return        
    morning = False
    noon = False
    afternoon = False
    evening = False
    night = False
    while True:
        if not done:
            while pause:
                pass
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
            elif int(hour) >= 22 or int(hour) <= 4:
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
            time.sleep(0.1)
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
                current_message = msgs["morning"]
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["morning"]) // 2), msgs["morning"], daycolor)
            elif noon:
                current_message = msgs["noon"]
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["noon"]) // 2), msgs["noon"], daycolor)
            elif afternoon:
                current_message = msgs["afternoon"]
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["afternoon"]) // 2), msgs["afternoon"], daycolor)
            elif evening:
                current_message = msgs["evening"]
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["evening"]) // 2), msgs["evening"], daycolor)
            elif night:
                current_message = msgs["night"]
                screens["main"].addstr(22, 0, bar, daycolor)
                screens["main"].addstr(22, width // 2 - (len(msgs["night"]) // 2), msgs["night"], daycolor)
            if not pause:
                screens["main"].refresh()
            
            time.sleep(0.1)
            if int(hour) == 23 and int(mins) == 59 and int(secs) == 59:
                with open(f"{conf_path}/clock.conf", "r") as file:
                    stuff = file.readlines()
                    for item in stuff:
                        times, msg = item.split("=")
                        msgs[times] = msg
                time.sleep(0.5)
            if current_message and current_message.strip() != "0":
                save(current_message)
        if done:
            break

def inps(screens, clock):
    while True:
        global done
        key = screens["main"].getch()
        if key == ord('\x1b'):
            done = 1
            clock.join()
            exit()
        elif key == ord("e"):
            view_times()

def view_times():
    global pause, msg_list
    pause = 1
    time.sleep(0.2)
    screens["main"].clear()
    view_list = []
    for item, state in all_messages.items():
        if state == "true":
            view_list.append(item)
        else:
            view_list.append("????")
    cache = []
    msg_list = print_list(0, globalpos, view_list)
    pos = 0
    while True:
        key = screens["main"].getch()
        if key == ord("w") or key == ord("s"):
            pos = select(pos, key, msg_list, view_list)
        elif key == ord("q"):
            break
        elif key == ord('\x1b'):
            exit()
    screens["main"].clear()
    pause = 0

def print_list(y, offset, menu):
    cache_list = []
    if not menu:
        menu = msg_list
    for item in menu:
        cache_list.append(item)
    if offset:
        screens["main"].clear()
        while offset != -1:
            cache_list.pop(offset)
            offset -= 1

    for item in cache_list:
        if y == height - 1:
            break
        screens["main"].addstr(y, 0, item)
        screens["main"].refresh()
        y += 1
    return cache_list

def select(pos, key, menu, view):
    global globalpos, msg_list
    if key == ord("s"):
        pos += 1
        if pos >= len(menu):
            pos -= 1
        back = 1
        if pos >= height - 2:
            globalpos += pos
            pos = 0
            back = 0
            msg_list = print_list(0, globalpos, view)
            return pos
    elif key == ord("w"):
        pos -= 1
        back = -1
        if pos < 0 and globalpos:
            globalpos -= height - 1
            if globalpos < 10:
                globalpos = 0
            pos = height - 2
            back = 0
            screens["main"].clear()
            msg_list = print_list(0, globalpos, view)
            return pos
        if pos < 0:
            pos = 0
    if len(menu) > 1:
        screens["main"].addstr(pos - back, 0, menu[pos - back])
    screens["main"].addstr(pos, 0, menu[pos], highlight)
    return pos
    
wrapper(main)
