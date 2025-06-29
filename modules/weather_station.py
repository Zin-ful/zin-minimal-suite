from machine import Pin, I2C
from bmp280 import BMP280
from ahtxx import AHT20 #also supports 10
from time import sleep
from os import listdir
i2c = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
sleep(0.1)
bmp = BMP280(i2c, addr=0x77) #may be 76 or 77 depending on module
aht = AHT20(i2c)

indoor = 0 #indoor climate stats
mode = 1 #0 = cel 1 = fare

time = 0
chance = 0 #trend of pressure
at = 0 #aht20 temp
ah = 0 #aht20 humid
bt = 0 #bmp280 temp
bp = 0 #bmp280 pressure
wait = 5 #time between temp checks (seconds), also devices when storm chances are calculated. Lower = sooner
seconds = 60 #all of this is for easy reading
minutes = 60 * seconds #time for storm chance, used to calc storm chance wait
stormchancewait = minutes // wait
bplist = []

if "time.txt" not in listdir() or "rst.txt" not in listdir():
    with open("time.txt", "w") as file:
        file.write("")
    with open("rst.txt", "w") as file:
            file.write("0")
with open("rst.txt", "r") as file:
        rst = file.read()
        rst = int(rst.strip())

if rst:
    with open("time.txt", "w") as file:
        file.write("")
    with open("rst.txt", "w") as file:
        file.write("0")
            
        
def ahtstats():
    global at, ah
    at = aht.temperature
    ah = aht.relative_humidity

def bmpstats():
    global bt, bp
    bt = bmp.temperature
    bp = bmp.pressure
    bp = bp / 100
    bplist.append(bp)

def reset():
    with open("rst.txt", "w") as file:
        file.write("1")

def stormchance():
    global chance
    if len(bplist) > 1:
        diffs = [bplist[i] - bplist[i + 1] for i in range(len(bplist) - 1)]
        chance = sum(diffs) / len(diffs)
    else:
        chance = 0
        

def forcast():
    temp = (bt + at) / 2
    print("**Data**")
    if not indoor:
        if temp < -30:
            tm = "Hazardously cold — extreme frostbite is likely within minutes. Avoid going outside."
        elif -30 <= temp <= -20:
            tm = "Severely cold — frostbite is very possible. Wear heavy protection."
        elif -20 < temp <= -10:
            tm = "Well below freezing — gloves and face protection are highly recommended."
        elif -10 < temp <= 0:
            tm = "Below freezing — dress in warm layers to avoid chill."
        elif 0 < temp <= 5:
            tm = "Cold — a jacket or coat is recommended."
        elif 5 < temp <= 10:
            tm = "Fairly cold — a light jacket or sweater should be enough."
        elif 10 < temp <= 15:
            tm = "Cool — sweater weather."
        elif 15 < temp <= 20:
            tm = "Mild — warming up nicely."
        elif 20 < temp <= 25:
            tm = "Comfortably warm — great summer weather."
        elif 25 < temp <= 30:
            tm = "Hot — try to stay cool and avoid direct sunlight for too long."
        elif 30 < temp <= 35:
            tm = "Very hot — stay hydrated and limit outdoor activity."
        elif 35 < temp <= 40:
            tm = "Extremely hot — likely a heatwave. Minimize time outdoors."
        elif temp > 40:
            tm = "Dangerously hot — heatstroke risk. Avoid going outside if possible."
        if not mode:
            print(f"Temperature is {temp}C")
            print(f"Dew point is {temp - ((100 - ah) / 5)}C")
        else:
            print(f"Temperature is {(temp * 1.8) + 32}F")
            print(f"Dew point is {((temp * 1.8) + 32) - ((100 - ah) / 5)}F")
        dp = temp - ((100 - ah) / 5)
        print(f"Humidity is {ah}%")
        print(f"Pressure is {bp}hPa")
        if chance < 0:
            print("Pressure is falling!")
            print(f"Downward pressure trend is {chance}")
        elif chance > 0:
            print("Pressure is rising!")
            print(f"Upwards pressure trend is {chance}")
        if ah < 30: #basic humidity
            ahm = "Very dry — increased risk of static electricity and dehydration."
        elif 30 <= ah < 60:
            ahm = "Comfortable humidity — air feels balanced and safe."
        elif 60 <= ah < 80:
            ahm = "Humid — stay hydrated; consider a dehumidifier indoors to avoid mold."
        elif ah >= 80:
            ahm = "Extremely humid — rain likely or very sticky conditions outdoors."

        if bp >= 1020: #basic pressure
            bpm = "High pressure — clear and calm weather likely."
        elif 1005 <= bp < 1020:
            bpm = "Moderate pressure — stable conditions, no major changes expected."
        elif bp < 1005:
            bpm = "Low pressure — unsettled weather or storms possible."

    elif indoor:
        if temp <= 10:
            tm = "Its farily cold, winter-like indoor climate"
        elif temp > 10 and temp <= 20:
            tm = "Good temps, combined with low humidity its a perfect indoor climate"
        elif temp > 20 and temp <= 30:
            tm = "Pretty warm, warmer indoor climate"
        elif temp > 30 and temp <= 40:
            tm = "It is extreamly hot inside"
        if not mode:
            print(f"Temperature is {temp}C")
        else:
            print(f"Temperature is {(temp * 1.8) + 32}F")
        
        print(f"Humidity is {ah}%")
        if ah < 30: #basic humidity
            ahm = "Its very dry inside"
        elif ah >= 30 and ah < 50:
            ahm = "Good indoor humidity"
        elif ah >= 50 and ah < 80:
            ahm = "Very humid, mold and dust mites are a concern if prolonged"
        elif ah >= 80:
            ahm = "Extreamly humid, you might have a waterleak somewhere or its just that humid"

        if bp:
            bpm = "No pressure readings for indoor climates."
    print("\n**Basic summary**")
    print(tm)
    print(ahm)
    print(bpm)
    
    #weather outlooks
    if not indoor:
        print("\n**Current weather**")
        if bp > 1020:
            if ah < 40:
                cast = "Sunny, dry, and clear — low humidity with high pressure suggests excellent visibility."
            elif ah < 60:
                cast = "Mostly sunny with mild humidity — comfortable conditions."
            else:
                cast = "Partly cloudy and slightly muggy — still fair due to high pressure."

        elif 1010 < bp <= 1020:
            if 50 <= ah <= 70:
                cast = "Cloudy and humid."
                if temp < 10:
                    cast += " Damp and cold outdoors."
                elif temp < 4:
                    cast += " Window frost/fog may start appearing"
                elif temp > 15:
                    cast += " Due to the humidity it may feel hotter than the ambient temperature"
                elif temp > 20:
                    cast += " Will feel very hot and sticky outside"
            elif ah < 50:
                cast = "Cloudy but dry — low chance of precipitation."
                if temp < 10:
                    cast += " Generally fair climate conditions."
                elif temp < 5:
                    cast += " May start to feel sort of bite-like with the closer to freezing temperatures."
                elif temp > 15:
                    cast += " Generally warm and fair climate conditions."
                elif temp > 20:
                    cast += " Pretty hot conditions with forested areas having slightly higher humidity."
            else:
                cast = "Cloudy with high humidity — weather could change."
                if temp > 28 and dp < temp - 5:
                    cast += " Storms are possible with a extremely low chance due to warmth and moisture with a high atmospheric pressure."
                elif temp > 28 and dp > temp - 5:
                    cast += " Storms are possible with a very low chance due to warmth, moisture, and high dew point with a high atmospheric pressure."
                elif temp > 28 and dp > temp - 5 and chance < -5:
                    cast += " Very low chances of future storms are possible in the next day or two due to warmth, moisture, high dew point, and a decreasing atmospheric pressure."
                elif temp > 28 and dp > temp - 5 and chance < -10:
                    cast += " Low chances of future storms are possible in the next day or two due to warmth, moisture, high dew point, and a heavily decreasing atmospheric pressure."
                elif temp < 15 and temp > 5 and dp < temp - 5:
                    cast += " Rain is possible with a extremely low chance due to moisture with a high atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5:
                    cast += " Rain is possible with a very low chance due to moisture and high dew point with a high atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5 and chance < -5:
                    cast += " Very low chances of future rain in the next day or two due to moisture, high dew point, and a decreasing atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5 and chance < -10:
                    cast += " Low chances of future rain is possible in the next day or two due to moisture, high dew point, and a heavily decreasing atmospheric pressure."
                elif temp < 5 and temp > 2 and dp < temp - 5:
                    cast += " Freezing rain is possible with a extremely low chance due to low temps, moisture with a high atmospheric pressure."
                elif temp < 5 and temp > 2 and dp > temp - 5:
                    cast += " Freezing rain is possible with a very low chance due to low temps, moisture and high dew point with a high atmospheric pressure."
                elif temp < 2 and dp < temp - 5:
                    cast += " Snow is possible with a extremely low chance due to low temps, moisture with a high atmospheric pressure."
                elif temp < 2 and dp > temp - 5:
                    cast += " Snow is possible with a very low chance due to low temps, moisture and high dew point with a high atmospheric pressure."
                elif temp < 2 and dp > temp - 5 and chance < -5:
                    cast += " Very low chances of future snow in the next day or two due to low temps, moisture, high dew point, and a decreasing atmospheric pressure."
                elif temp < 2 and dp > temp - 5 and chance < -10:
                    cast += " Low chances of future snow is possible in the next day or two due to low temps, moisture, high dew point, and a heavily decreasing atmospheric pressure."
        elif 1000 < bp <= 1010:
            if ah >= 70:
                cast = "Humid and cloudy — rain is possible."
                if temp < 2:
                    cast += " Snow is possible."
                elif 2 <= temp <= 10:
                    cast += " Fog is likely."
                elif temp > 28 and dp < temp - 5:
                    cast += " Storms are possible with a low chance due to warmth and moisture with an average atmospheric pressure."
                elif temp > 28 and dp > temp - 5:
                    cast += " Storms are possible with a moderate-low chance due to warmth, moisture, and high dew point with average atmospheric pressure."
                elif temp > 28 and dp > temp - 5 and chance < -5:
                    cast += " Moderate-low chance of future storms that are possible in the next day or two due to warmth, moisture, high dew point, and a decreasing atmospheric pressure."
                elif temp > 28 and dp > temp - 5 and chance < -10:
                    cast += " Moderate chance of future storms are possible in the next day or two due to warmth, moisture, high dew point, and a heavily decreasing atmospheric pressure."
                elif temp < 15 and temp > 5 and dp < temp - 5:
                    cast += " Rain is possible with a low chance due to moisture with a average atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5:
                    cast += " Rain is possible with a moderate-low chance due to moisture and high dew point with a average atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5 and chance < -5:
                    cast += " Low chances of future rain in the next day or two due to moisture, high dew point, and an average decreasing atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5 and chance < -10:
                    cast += " Moderate chances of future rain is possible in the next day or two due to moisture, high dew point, and an average heavily decreasing atmospheric pressure."
                elif temp < 5 and temp > 2 and dp < temp - 5:
                    cast += " Freezing rain is possible with a low chance due to low temps, moisture with a average atmospheric pressure."
                elif temp < 5 and temp > 2 and dp > temp - 5:
                    cast += " Freezing rain is possible with a moderate-low chance due to low temps, moisture and high dew point with a average atmospheric pressure."
                elif temp < 2 and dp < temp - 5:
                    cast += " Snow is possible with a low chance due to low temps, moisture with a average atmospheric pressure."
                elif temp < 2 and dp > temp - 5:
                    cast += " Snow is possible with a moderate-low chance due to low temps, moisture and high dew point with a average atmospheric pressure."
                elif temp < 2 and dp > temp - 5 and chance < -5:
                    cast += " Low chances of future snow in the next day or two due to low temps, moisture, high dew point, and an average decreasing atmospheric pressure."
                elif temp < 2 and dp > temp - 5 and chance < -10:
                    cast += " Moderate-low chances of future snow is possible in the next day or two due to low temps, moisture, high dew point, and an average heavily decreasing atmospheric pressure."
            elif 40 <= ah < 70:
                cast = "Mildly humid — typical conditions for the season."
                if temp > 30:
                    cast += " Hot and dry — storms are unlikely."
                elif 20 <= temp <= 30 and dp < temp - 10:
                    cast += " Warm but dry — rain unlikely."
                elif 10 <= temp < 20 and dp < temp - 10:
                    cast += " Pleasant with low moisture — unlikely to rain."
                elif temp < 10 and dp > temp - 5:
                    cast += " Cool and calm — slight chance of fog or mist."
                elif temp < 2 and dp > temp - 5:
                    cast += " Cold with limited moisture — light snow possible but not likely."

            elif ah < 40:
                cast = "Dry conditions — clear skies likely."
                if temp > 30:
                    cast += " Hot and arid — no precipitation expected."
                elif 15 < temp <= 30:
                    cast += " Warm and dry — low chance of any clouds or rain."
                elif 5 < temp <= 15:
                    cast += " Cool and crisp — dry air dominates."
                elif temp <= 5:
                    cast += " Cold and dry — unlikely to snow due to lack of moisture."

            else:
                cast = "Unstable conditions — shifting weather possible."

        elif bp <= 1000:
            if ah >= 70:
                cast = "Very humid — rain is likely."
                if temp > 24 and dp < temp - 5:
                    cast = "Very humid and warm — Thunderstorms and rain likely."
                elif temp > 25 and dp > temp - 5:
                    cast = "Very humid and warm — Thunderstorms are very likely."
                elif temp > 25 and dp > temp - 5 and chance < -5:
                    cast = "Good chance of future storms in the next 12-24 hours due to low atmospheric pressure, warmth, moisture, high dew point, and an already low decreasing pressure."
                elif temp > 25 and dp > temp - 5 and chance < -10:
                    cast = " High chance of future storms in the next 12-24 hours due to low atmospheric pressure, warmth, moisture, high dew point, and an already low heavily decreasing pressure."
                elif temp < 15 and temp > 5 and dp < temp - 5:
                    cast += " Rain is possible with a moderate chance due to moisture with a low atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5:
                    cast += " Rain is possible with a high chance due to moisture and high dew point with a low atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5 and chance < -5:
                    cast += " Moderate chances of future rain in the next day or two due to moisture, high dew point, and a low and decreasing atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5 and chance < -10:
                    cast += " High chances of future rain is possible in the next day or two due to moisture, high dew point, and a low heavily decreasing atmospheric pressure."
                elif temp < 5 and temp > 2 and dp < temp - 5:
                    cast += " Freezing rain is possible with a moderate chance due to low temps and moisture with a low atmospheric pressure."
                elif temp < 5 and temp > 2 and dp > temp - 5:
                    cast += " Freezing rain is possible with a high chance due to low temps, moisture and low dew point with a low atmospheric pressure."
                elif temp < 2 and dp < temp - 5:
                    cast += " Snow is possible with a moderate chance due to low temps and moisture with a low atmospheric pressure."
                elif temp < 2 and dp > temp - 5:
                    cast += " Snow is possible with a high chance due to low temps, moisture and high dew point with a low atmospheric pressure."
                elif temp < 2 and dp > temp - 5 and chance < -5:
                    cast += " Moderate chances of future snow in the next day or two due to low temps, moisture, high dew point, and a low decreasing atmospheric pressure."
                elif temp < 2 and dp > temp - 5 and chance < -10:
                    cast += " High chances of future snow is possible in the next day or two due to low temps, moisture, high dew point, and a low and heavily decreasing atmospheric pressure."
            
            elif 40 <= ah < 70:
                cast = "Mildly humid — typical seasonal conditions."
                if temp > 30:
                    cast += " Hot and dry — no storms expected under current pressure."
                elif 20 <= temp <= 30:
                    if dp < temp - 10:
                        cast += " Warm but dry — skies likely to stay clear."
                    elif dp > temp - 5:
                        cast += " Warm with moderate moisture — clouds possible, but rain unlikely."
                elif 10 <= temp < 20:
                    cast += " Pleasant and slightly humid — stable conditions."
                elif temp < 10:
                    if dp > temp - 5:
                        cast += " Cool and slightly damp — patchy mist or dew is possible overnight."
                    else:
                        cast += " Cool and dry — little weather activity expected."
            elif ah < 40:
                cast = "Dry conditions — fair weather expected."
                if temp > 30:
                    cast += " Hot and arid — clear skies dominate."
                elif 15 < temp <= 30:
                    cast += " Warm and dry — no precipitation expected."
                elif 5 < temp <= 15:
                    cast += " Cool and dry — crisp, clear weather likely."
                elif temp <= 5:
                    cast += " Cold and dry — snow very unlikely due to insufficient moisture."
        else:
            cast = "Unable to determine weather — sensor data unclear."
    elif indoor:
        print("\n**Indoor conditions**")
        if temp < 16:
            cast = "Indoor temperature is cold."
            if ah < 30:
                cast += " Air is also very dry — consider a humidifier and additional heating."
            elif ah > 60:
                cast += " It's cold and humid — may feel clammy or cause condensation."
            else:
                cast += " Dry but tolerable. Consider light heating for comfort."

        elif temp >= 16 and temp < 21:
            cast = "Indoor temperature is cool."
            if ah < 30:
                cast += " Air is dry — consider increasing humidity slightly."
            elif ah > 60:
                cast += " May feel cooler than it is due to higher humidity."
            else:
                cast += " Comfortable for most people, especially when active."

        elif temp >= 21 and temp < 25:
            cast = "Indoor temperature is comfortable."
            if ah < 30:
                cast += " Slightly dry air — may cause skin or throat dryness."
            elif ah > 60:
                cast += " May feel a bit muggy — ventilation could help."
            else:
                cast += " Ideal indoor climate."

        elif temp >= 25 and temp < 28:
            cast = "Indoor temperature is warm."
            if ah < 30:
                cast += " Dry heat — monitor for dehydration or static electricity."
            elif ah > 60:
                cast += " Humid and warm — could be uncomfortable without airflow."
            else:
                cast += " Warm but generally tolerable."

        elif temp >= 28:
            cast = "Indoor temperature is hot."
            if ah < 30:
                cast += " Air is hot and dry — risk of dehydration or discomfort."
            elif ah > 60:
                cast += " Air is hot and humid — high discomfort and potential for mold."
            else:
                cast += " Consider cooling — heat may cause fatigue."

        else:
            cast = "Unable to determine indoor comfort — values may be out of range."
    print(cast)
while True:
    if time >= stormchancewait * 1.5:
        with open("time.txt", "w") as file:
            file.write("")
        stormchance()
    ahtstats()    
    bmpstats()
    forcast()
    with open("time.txt", "r") as file:
        time = file.read()
    if not time:
        time = 1
    else:
        time = int(time.strip())
        time += 1
    with open("time.txt", "w") as file:
        file.write(str(time))
    print(time)
    sleep(wait)