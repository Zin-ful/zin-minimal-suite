from machine import Pin, I2C
from bmp280 import BMP280
from ahtxx import AHT20 #also supports 10
from time import sleep
from os import listdir
import ssd1306
i2c = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
screeni2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
sleep(0.1)
bmp = BMP280(i2c, addr=0x77) #may be 76 or 77 depending on module
aht = AHT20(i2c)
display = ssd1306.SSD1306_I2C(128, 64, screeni2c)

indoor = 0 #indoor climate stats
mode = 1 #0 = cel 1 = fare

time = 0
chance = 0 #trend of pressure
at = 0 #aht20 temp
ah = 0 #aht20 humid
bt = 0 #bmp280 temp
bp = 0 #bmp280 pressure
wait = 500 #time between temp checks (seconds), also devices when storm chances are calculated. Lower = sooner

stormchancewait = 30 #"wait" increaments a counter, once a counter reaches this variable it will check the current forecast
#stormchancewait will assist in future forecasts that are 1-6 hours ahead. the ideal value is going to be 30 for a 2-3 hour delay between forcasts of immediate weather

timepass = 0 #overall time passed
cast12wait = 30 #timepass counts to the following values to predict weather conditions that amount of time in the future
cast24wait = cast12wait * 2
cast48wait = cast24wait * 2
bplist = []
castplus = None
cast12 = 0 #pressure trend
cast24 = 0 #pressure trend
cast48 = 0 #pressure trend
cast12m = ""
cast24m = ""
cast48m = ""
temp = 0
dp = 0

if "time.txt" not in listdir() or "rst.txt" not in listdir() or "timepass.txt" not in listdir():
    with open("time.txt", "w") as file:
        file.write("")
    with open("timepass.txt", "w") as file:
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
    with open("timepass.txt", "w") as file:
        file.write("")
    with open("history.txt", "w") as file:
        file.write("")
            
        
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
    global chance, castplus, timepass, cast12, cast24, cast48, cast12m, cast24m, cast48m
    hour24 = []
    hour48 = []
    hour12 = []
    
    if timepass == cast12wait:
        future = "6-12"
        with open("history.txt", "r") as file:
            for item in file.readlines():
                item = item.strip().strip('\n')
                hour12.append(float(item))
    elif timepass == cast24wait:
        future = "12-24"
        with open("history.txt", "r") as file:
            for item in file.readlines():
                item = item.strip().strip('\n')
                hour24.append(float(item))
            print(file.read())
    elif timepass == cast48wait:
        future = "24-48"
        with open("history.txt", "r") as file:
            for item in file.readlines():
                item = item.strip().strip('\n')
                hour48.append(float(item))
            print(file.read())
        with open("history.txt", "w") as file:
            file.write("")
        with open("timepass.txt", "w") as file:
            file.write("")
            timepass = 0

    else:
        future = "the next hour"

    if len(bplist) > 1:
        diffs = [bplist[i] - bplist[i + 1] for i in range(len(bplist) - 1)]
        chance = sum(diffs) / len(diffs)
        chance = round(chance, 5)
    else:
        chance = 0
    if hour12 and len(hour12) > 1:
        diffs = [hour12[i] - hour12[i + 1] for i in range(len(hour12) - 1)]
        chance = sum(diffs) / len(diffs)
        chance = round(chance, 5)
        cast12 = chance
    elif hour24 and len(hour24) > 1:
        diffs = [hour24[i] - hour24[i + 1] for i in range(len(hour24) - 1)]
        chance = sum(diffs) / len(diffs)
        chance = round(chance, 5)
        cast24 = chance
    elif hour48 and len(hour48) > 1:
        diffs = [hour48[i] - hour48[i + 1] for i in range(len(hour48) - 1)]
        chance = sum(diffs) / len(diffs)
        chance = round(chance, 5)
        cast48 = chance
    with open("history.txt", "a") as file:
        file.write(str(chance) + "\n")

    if 1010 < bp <= 1025:
        if ah >= 70:
            castplus = f"The next {future} hours will be partly cloudy but mostly clear. Conditions should be stable."
            if temp < 2 and dp < temp - 5 and chance < -2:
                castplus += f"\nAlmost no chance of snow within the next {future} hours."
            elif temp < 2 and dp > temp - 5 and chance < -2:
                castplus += f"\nAlmost no chance of snow within the next {future} hours, expect frost on windows and other surfaces and stable weather conditions."
            elif temp < 2 and dp < temp - 5 and chance < -6:
                castplus += f"\nLow chances of isolated light snow showers is possible in the next {future} hours."
            elif temp < 2 and dp > temp - 5 and chance < -6:
                castplus += f"\nLow chances of light snow showers is possible in the next {future} hours. The dew point is high enough to frost plants and windows, and the climate may become unstable"
            elif temp < 2 and dp < temp - 5 and chance < -12:
                castplus += f"\nChances of isolated snow showers in {future} hours. Local climate is becoming increasingly unstable, possible moderate snow could be moving in."
            elif temp < 2 and dp > temp - 5 and chance < -12:
                castplus += f"\nChances of snow showers in {future} hours. Local climate is becoming increasingly unstable, the dew point is high enough to energize incoming and local stormfronts."
            
            if temp > 2 and temp <= 24 and dp < temp - 5 and chance < -2:
                castplus += f"Update: Almost no chance of rain within the next {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -2:
                castplus += f"\nAlmost no chance of rain within the next {future} hours, expect condensation on cool surfaces and stable conditions."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -6:
                castplus += f"\nLow chances of isolated light rain is possible in the next {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -6:
                castplus += f"\nLow chances of light rain is possible in the next {future} hours. The decreasing atmospheric pressure can turn conditions unstable."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -12:
                castplus += f"\nChances of isolated rain showers in {future} hours. Local climate is becoming increasingly unstable, possible moderate rain could be moving in."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -12:
                castplus += f"\nChances of rain showers in {future} hours. Local climate is becoming increasingly unstable, the dew point is high enough to energize incoming and local stormfronts."
            
            if temp > 24 and dp < temp - 5 and chance < -2:
                castplus += f"Update: Almost no chance of thunder or rain within the next {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -2:
                castplus += f"\nAlmost no chance of thunder or rain within the next {future} hours."
            elif temp > 24 and dp < temp - 5 and chance < -6:
                castplus += f"\nChances of light rain and isolated thunder storms is possible in the next {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -6:
                castplus += f"\nChances of light rain and storms is possible in the next {future} hours. Expect unsettled weather and possible rapid changes"
            elif temp > 24 and dp < temp - 5 and chance < -12:
                castplus += f"\nIncreasing chances of moderate rain and thunder in {future} hours. Local climate is increasingly unstable, possible increasing rain and thunder."
            elif temp > 24 and dp > temp - 5 and chance < -12:
                castplus += f"\nIncreasing chances of moderate rain and thunder in {future} hours. Local climate is increasingly unstable, existing weather could worsen."
            else:
                castplus += " No weather changes"
        
        elif ah <= 70 and ah > 40:
            castplus = f"The next {future} hours will be mostly clear with very stable conditions."
            if temp < 2 and dp < temp - 5 and chance < -4:
                castplus += f"\nAlmost no chance of snow within the next {future} hours, expect a more comfortable cold condition."
            elif temp < 2 and dp > temp - 5 and chance < -6:
                castplus += f"\nExtremely low chance of snow within the next {future} hours."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -4:
                castplus += f"\nExtremely low chance of isolated rain showers in {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -8:
                castplus += f"\nExtremely low chance of rain showers in {future} hours. Local climate is becoming more unstable."
            elif temp > 24 and dp < temp - 5 and chance < -4:
                castplus += f"\nAlmost no chance of rain and thunder in {future} hours. Local climate is becoming more unstable."
            elif temp > 24 and dp > temp - 5 and chance < -8:
                castplus += f"\nExtremely low chances of moderate rain and thunder in {future} hours. Local climate is more unstable, isolated light rain is possible"
        elif ah < 40:
            castplus += f"The next {future} hours should be dry and clear."
            if temp < 2 and chance < -4:
                castplus += f"\nNo chance of snow within the next {future} hours."
            elif temp < 2 and chance < -6:
                castplus += f"\nAlmost no chance of snow within the next {future} hours, expect a dry cold condition."
            elif temp > 2 and temp <= 24 and chance < -4:
                castplus += f"\nNo chance of rain showers in {future} hours."
            elif temp > 2 and temp <= 24 and chance < -8:
                castplus += f"\nAlmost no chance of rain showers in {future} hours. Local climate is becoming mildly unstable."
            elif temp > 24 and chance < -4:
                castplus += f"\nNo chance of moderate rain and thunder in {future} hours."
            elif temp > 24 and chance < -8:
                castplus += f"\nAlmost no chance of moderate rain and thunder in {future} hours. Local climate is becoming mildly unstable."
        else:
            castplus += " No weather changes"
    elif 1000 < bp <= 1010:
        if ah >= 70:
            castplus = f"The next {future} hours will humid and cloudy, climate is mildly unsettled"
            if temp < 2 and dp < temp - 5 and chance < -2:
                castplus += f"\nChance of snow within the next {future} hours."
            elif temp < 2 and dp > temp - 5 and chance < -2:
                castplus += f"\nChance of snow within the next {future} hours, expect frost on windows and other surfaces."
            elif temp < 2 and dp < temp - 5 and chance < -6:
                castplus += f"\nModerate to high chances of snow is possible in the next {future} hours."
            elif temp < 2 and dp > temp - 5 and chance < -6:
                castplus += f"\nModerate to high chances of snow is possible in the next {future} hours. The climate is increasingly unstable, watch out for changing weather and worsening snow fall."
            elif temp < 2 and dp < temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy snow in {future} hours. Local climate is becoming very unstable, possible snow storms could be moving in."
            elif temp < 2 and dp > temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy snow in {future} hours. Local climate is becoming very unstable, current stormfronts may worsen or become severe."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -2:
                castplus += f"\nChance of rain within the next {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -2:
                castplus += f"\nChance of rain within the next {future} hours, expect condensation on cool surfaces and stable conditions."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -6:
                castplus += f"\nModerate to high chances of rain is possible in the next {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -6:
                castplus += f"\nModerate to high chances of rain is possible in the next {future} hours. The decreasing atmospheric pressure can turn conditions unstable."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy rain showers in {future} hours. Local climate is becoming extreamly unstable, possible heavy rain could be moving in."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy rain showers in {future} hours. Local climate is becoming extreamly unstable, current stormfronts could significantly worsen."
            elif temp > 24 and dp < temp - 5 and chance < -2:
                castplus += f"Moderate to high chances of thunder or rain within the next {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -2:
                castplus += f"\nModerate to high chances of thunder or rain within the next {future} hours."
            elif temp > 24 and dp < temp - 5 and chance < -6:
                castplus += f"\nIncreasing chances of rain and thunder storms is possible in the next {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -6:
                castplus += f"\nIncreasing chances of moderate to heavy rain and storms is possible in the next {future} hours. Expect unsettled weather and possible rapid changes"
            elif temp > 24 and dp < temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy rain and thunder in {future} hours. Local climate is increasingly unstable, current weather conditions could worsen."
            elif temp > 24 and dp > temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy rain and thunder in {future} hours. Local climate is extreamly unstable, existing weather could turn severe."
            else:
                castplus += " Climate is mildly unstable"
        elif ah <= 70 and ah > 40:
            castplus = f"The next {future} hours will be mostly clear with mildly stable conditions."
            if temp < 2 and dp < temp - 5 and chance < -4:
                castplus += f"\nExtremely low chance of snow within the next {future} hours, expect a more comfortable cold condition."
            elif temp < 2 and dp > temp - 5 and chance < -6:
                castplus += f"\nVery low chance of snow within the next {future} hours, this could change with light snow showers."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -4:
                castplus += f"\nVery low isolated rain showers in {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -8:
                castplus += f"\nVery low of rain showers in {future} hours. Local climate is becoming more unstable, light rain showers are possible."
            elif temp > 24 and temp - 5 and chance < -4:
                castplus += f"\nExtremely low chance of rain and thunder in {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -8:
                castplus += f"\nVery low chances of rain and thunder in {future} hours. Local climate is becoming more unstable, possible light to moderate isolated rain showers."
        elif ah < 40:
            castplus = f"The next {future} hours should be dry and clear."
            if temp < 2 and chance < -4:
                castplus += f"\nAlmost no chance of snow within the next {future} hours, expect a dry cold condition."
            elif temp < 2 and chance < -6:
                castplus += f"\nExtreamly low chance of snow within the next {future} hours."
            elif temp > 2 and temp <= 24 and chance < -4:
                castplus += f"\nAlmost no chance of rain showers in {future} hours."
            elif temp > 2 and temp <= 24 and chance < -8:
                castplus += f"\nExtreamly low chance of rain showers in {future} hours. Local climate is becoming mildly unstable."
            elif temp > 24 and chance < -4:
                castplus += f"\nAlmost no chance of rain and thunder in {future} hours."
            elif temp > 24 and chance < -8:
                castplus += f"\nExtreamly low chance of rain and thunder in {future} hours. Local climate is becoming mildly unstable."
        else:
            castplus = "No weather changes"
    
    elif bp <= 1000:
        if ah >= 70:
            castplus = f"The next {future} hours will humid with high cloud coverage with a very unstable climate."
            if temp < 2 and dp < temp - 5 and chance < -2:
                castplus += f"\nHigh chance of snow within the next {future} hours."
            elif temp < 2 and dp > temp - 5 and chance < -2:
                castplus += f"\nHigh chance of snow within the next {future} hours."
            elif temp < 2 and dp < temp - 5 and chance < -6:
                castplus += f"\nHigh chances of heavy snow is possible in the next {future} hours."
            elif temp < 2 and dp > temp - 5 and chance < -6:
                castplus += f"\nHigh chances of heavy snow is possible in the next {future} hours. The climate is very unstable, watch out for changing weather and worsening snow fall."
            elif temp < 2 and dp < temp - 5 and chance < -12:
                castplus += f"\nVery high chances of heavy snow in {future} hours. Local climate is extremely unstable and conditions may become severe."
            elif temp < 2 and dp > temp - 5 and chance < -12:
                castplus += f"\nVery high chances of very heavy snow in {future} hours. Local climate is extremely unstable, current stormfronts can worsen or become severe."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -2:
                castplus += f"\nHigh chance of rain and possbily thunder within the next {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -2:
                castplus += f"\nHigh chance of rain and possible thunder within the next {future} hours, expect condensation on cool surfaces and stable conditions."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -6:
                castplus += f"\nHigh chances of heavy rain and possible thunder in the next {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -6:
                castplus += f"\nHigh chances of heavy rain and possible thunder in the next {future} hours. The climate is very unstable, weather can rapidy change or worsen."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy rain and possible thunder in {future} hours. Local climate is extremely unstable, possible heavy thunder could be moving in."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -12:
                castplus += f"\nHigh chances of heavy rain and possible thunder {future} hours. Local climate is extremely unstable, current or future storms could significantly worsen."
            elif temp > 24 and dp < temp - 5 and chance < -2:
                castplus += f"\nHigh chances of thunder or rain within the next {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -2:
                castplus += f"\nHigh chances of thunder or rain within the next {future} hours."
            elif temp > 24 and dp < temp - 5 and chance < -6:
                castplus += f"\nVery high chances of rain and thunder storms is possible in the next {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -6:
                castplus += f"\nVery high chances of heavy rain and storms is possible in the next {future} hours. Expect the possibility of severe weather and possible rapid changes"
            elif temp > 24 and dp < temp - 5 and chance < -12:
                castplus += f"\nVery high hances of heavy rain and thunder in {future} hours. Local climate is extremely unstable, current or future storms could worsen"
            elif temp > 24 and dp > temp - 5 and chance < -12:
                castplus += f"\nVery high chances of heavy rain and thunder in {future} hours. Local climate is extremely unstable, existing weather could turn severe."
            elif chance > 4:
                castplus += f"\nCurrent weather should be mildly more stable and any current cloud coverage or bad weather should be clearing in the next {future} hours, possibly longer"
            elif chance > 4:
                castplus += f"\nCurrent weather should be stablizing and any current cloud coverage or bad weather should be clearing in the next {future} hours"
            elif chance > 6:
                castplus += f"\nCurrent weather should be increasingly stable and any current cloud coverage or bad weather should be clearing pretty soon"
        elif ah <= 70 and ah > 40:
            castplus = f"The next {future} hours will be mostly cloudy with unstable conditions."
            if temp < 2 and dp < temp - 5 and chance < -4:
                castplus += f"\nModerate chance of snow within the next {future} hours, expect cold conditions."
            elif temp < 2 and dp > temp - 5 and chance < -6:
                castplus += f"\nModerate to high chance of snow within the next {future} hours, this could change."
            elif temp > 2 and temp <= 24 and dp < temp - 5 and chance < -4:
                castplus += f"\nModerate isolated rain showers in {future} hours."
            elif temp > 2 and temp <= 24 and dp > temp - 5 and chance < -8:
                castplus += f"\nModerate to high of rain showers in {future} hours. Local climate is unstable, moderate rain showers are possible."
            elif temp > 24 and temp - 5 and chance < -4:
                castplus += f"\nModerate chance of rain and possibly thunder in {future} hours."
            elif temp > 24 and dp > temp - 5 and chance < -8:
                castplus += f"\nModerate to high chances of rain and possibly thunder in {future} hours. Local climate is more unstable, possible moderate isolated rain showers."
        elif ah < 40:
            castplus = f"The next {future} hours should be dry and cloudy."
            if temp < 2 and chance < -4:
                castplus += f"\nLow chance of snow within the next {future} hours, expect a dry cold condition."
            elif temp < 2 and chance < -6:
                castplus += f"\nLow chance of snow within the next {future} hours."
            elif temp > 2 and temp <= 24 and chance < -4:
                castplus += f"\nLow chance of rain showers in {future} hours."
            elif temp > 2 and temp <= 24 and chance < -8:
                castplus += f"\nLow chance of rain showers in {future} hours. Local climate is unstable."
            elif temp > 24 and chance < -4:
                castplus += f"\nLow chance of rain and thunder in {future} hours."
            elif temp > 24 and chance < -8:
                castplus += f"\nLow chance of rain and thunder in {future} hours. Local climate is unstable."
        else:
            castplus += " No weather changes"
    else:
        castplus = "No weather changes"
    if timepass == cast12wait:
        cast12m = castplus
        with open("12.txt","a") as file:
            file.write(cast12m)
    elif timepass == cast24wait:
        cast24m = castplus
        with open("24.txt","a") as file:
            file.write(cast24m)
    elif timepass == cast48wait:
        cast48m = castplus
        with open("48.txt","a") as file:
            file.write(cast48m)

def forcast():
    global temp, dp
    temp = at #(bt + at) / 2
    print("\n**Data**")
    if not indoor:
        if temp < -30:
            tm = "Hazardously cold - extreme frostbite is likely within minutes. Avoid going outside."
        elif -30 <= temp <= -20:
            tm = "Severely cold - frostbite is very possible. Wear heavy protection."
        elif -20 < temp <= -10:
            tm = "Well below freezing - gloves and face protection are highly recommended."
        elif -10 < temp <= 0:
            tm = "Below freezing - dress in warm layers to avoid chill."
        elif 0 < temp <= 5:
            tm = "Cold - a jacket or coat is recommended."
        elif 5 < temp <= 10:
            tm = "Fairly cold - a light jacket or sweater should be enough."
        elif 10 < temp <= 15:
            tm = "Cool - sweater weather."
        elif 15 < temp <= 20:
            tm = "Mild - warming up nicely."
        elif 20 < temp <= 28:
            tm = "Comfortably warm - great summer weather."
        elif 28 < temp <= 33:
            tm = "Hot - try to stay cool and avoid direct sunlight for too long."
        elif 33 < temp <= 38:
            tm = "Very hot - stay hydrated and limit outdoor activity."
        elif 38 < temp <= 43:
            tm = "Swealtering - likely a heatwave. Minimize time outdoors."
        elif temp > 43:
            tm = "Dangerously hot - heatstroke risk. Avoid going outside if possible."
        if not mode:
            print(f"Temperature is {temp}C")
            print(f"Dew point is {temp - ((100 - ah) / 5)}C")
        else:
            print(f"Temperature is {(1.8 * temp) + 32}F")
            print(f"Dew point is {((1.8 * temp) + 32) - ((100 - ah) / 5)}F")
        dp = temp - ((100 - ah) / 5)
        print(f"Humidity is {ah}%")
        print(f"Pressure is {bp}hPa")
        if chance < 0:
            print("Pressure is falling.")
            print(f"Downward pressure trend is {chance}")
        elif chance > 0:
            print("Pressure is rising.")
            print(f"Upwards pressure trend is {chance}")
        if ah < 30: #basic humidity
            ahm = "Very dry - the low humidity increases fire risk in some areas as well as dry skin and eyes."
        elif 30 <= ah < 60:
            ahm = "Comfortable humidity - air feels balanced and safe."
        elif 60 <= ah < 80:
            ahm = "Humid - stay hydrated; consider a dehumidifier indoors to avoid mold."
        elif ah >= 80:
            ahm = "Extremely humid - Very sticky conditions outdoors."

        if bp >= 1020: #basic pressure
            bpm = "High pressure - clear and calm weather likely."
        elif 1010 <= bp < 1020:
            bpm = "Moderate pressure - stable conditions, no major changes expected."
        elif 1000 <= bp < 1010:
            bpm = "Moderate-low pressure  - less stable, minor changes possible."
        elif bp < 1000:
            bpm = "Low pressure - unstable weather, storms likely with the right condition."

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
                cast = "Sunny, dry, and clear - low humidity with high pressure suggests excellent visibility."
            elif ah < 60:
                cast = "Mostly sunny with mild humidity - comfortable conditions."
            else:
                cast = "Possibly cloudy although sparce and slightly muggy - still fair due to high pressure."

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
                cast = "Cloudy but dry - low chance of precipitation."
                if temp < 10:
                    cast += " Generally fair climate conditions."
                elif temp < 5:
                    cast += " May start to feel sort of bite-like with the closer to freezing temperatures."
                elif temp > 15:
                    cast += " Generally warm and fair climate conditions."
                elif temp > 20:
                    cast += " Pretty hot conditions with forested areas having slightly higher humidity."
            else:
                cast = "Cloudy with high humidity - stable, weather could change but its not likely."
                if temp < 2 and dp < temp - 5:
                    cast += " Snow is not very possible due to low temps and moisture with a high atmospheric pressure."
                elif temp < 2 and dp > temp - 5:
                    cast += " Snow is possible due to low temps, moisture and high dew point with a high atmospheric pressure."
                elif temp < 5 and temp > 2 and dp < temp - 5:
                    cast += " Freezing rain is not very possible low chance due to low temps and moisture with a high atmospheric pressure."
                elif temp < 5 and temp > 2 and dp > temp - 5:
                    cast += " Freezing rain is possible due to low temps, moisture and high dew point with a high atmospheric pressure."
                elif temp < 15 and temp > 5 and dp < temp - 5:
                    cast += " Rain is not very possible due to moisture with a high atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5:
                    cast += " Rain is possible due to moisture and high dew point with a high atmospheric pressure."
                elif temp > 28 and dp < temp - 5:
                    cast += " Storms are possible due to warmth and moisture with a high atmospheric pressure."
                elif temp > 28 and dp > temp - 5:
                    cast += " Storms are possible due to warmth, moisture, and high dew point with a high atmospheric pressure."

        elif 1000 < bp <= 1010:
            if ah >= 70:
                cast = "Humid and cloudy."
                if temp < 2:
                    cast += " Snow is possible."
                elif temp < 2 and dp < temp - 5:
                    cast += " Snow is not very possible due to low temps, moisture with a average atmospheric pressure."
                elif temp < 2 and dp > temp - 5:
                    cast += " Snow is not very possible due to low temps, moisture and high dew point with a average atmospheric pressure."
                elif temp < 5 and temp > 2 and dp < temp - 5:
                    cast += " Freezing rain is not very possible due to low temps, moisture with a average atmospheric pressure."
                elif temp < 5 and temp > 2 and dp > temp - 5:
                    cast += " Freezing rain is possible due to low temps, moisture and high dew point with a average atmospheric pressure."
                elif temp < 15 and temp > 5 and dp < temp - 5:
                    cast += " Rain is not very possible due to moisture with a average atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5:
                    cast += " Rain is possible due to moisture and high dew point with a average atmospheric pressure."
                elif temp > 28 and dp < temp - 5:
                    cast += " Storms are possible due to warmth and moisture with an average atmospheric pressure."
                elif temp > 28 and dp > temp - 5:
                    cast += " Storms are possible due to warmth, moisture, and high dew point with average atmospheric pressure."
                elif 2 <= temp <= 10:
                    cast += " Fog is likely."
  
            elif 40 <= ah < 70:
                cast = "Mildly humid - typical conditions for the season."
                if temp < 2 and dp < temp - 10:
                    cast += " Cold with limited moisture - light snow possible but not likely."
                elif temp < 10 and dp > temp - 5:
                    cast += " Cool and calm - slight chance of fog or mist."
                elif 10 <= temp < 20 and dp < temp - 10:
                    cast += " Pleasant with low moisture - unlikely to rain."
                elif 20 <= temp <= 30 and dp < temp - 10:
                    cast += " Warm but dry - rain unlikely."
                elif temp > 30:
                    cast += " Hot and dry - storms are unlikely."

            elif ah < 40:
                cast = "Dry conditions - clear skies likely."
                if temp > 30:
                    cast += " Hot and arid - no precipitation expected."
                elif 15 < temp <= 30:
                    cast += " Warm and dry - low chance of any clouds or rain."
                elif 5 < temp <= 15:
                    cast += " Cool and crisp - dry air dominates."
                elif temp <= 5:
                    cast += " Cold and dry - unlikely to snow due to lack of moisture."

            else:
                cast = "Unstable conditions - shifting weather possible."

        elif bp <= 1000:
            if ah >= 70:
                cast = "Very humid - rain is likely."
                if temp > 24 and dp < temp - 5:
                    cast = "Very humid and warm - Thunderstorms and rain possible."
                elif temp > 25 and dp > temp - 5:
                    cast = "Very humid and warm - Thunderstorms are possible."
                elif temp < 15 and temp > 5 and dp < temp - 5:
                    cast += " Rain is possible due to moisture with a low atmospheric pressure."
                elif temp < 15 and temp > 5 and dp > temp - 5:
                    cast += " Rain is possible due to moisture and high dew point with a low atmospheric pressure."
                elif temp < 5 and temp > 2 and dp < temp - 5:
                    cast += " Freezing rain is possible due to low temps and moisture with a low atmospheric pressure."
                elif temp < 5 and temp > 2 and dp > temp - 5:
                    cast += " Freezing rain is possible due to low temps, moisture and low dew point with a low atmospheric pressure."
                elif temp < 2 and dp < temp - 5:
                    cast += " Snow is possible due to low temps and moisture with a low atmospheric pressure."
                elif temp < 2 and dp > temp - 5:
                    cast += " Snow is possible due to low temps, moisture and high dew point with a low atmospheric pressure."
            elif 40 <= ah < 70:
                cast = "Mildly humid - typical seasonal conditions."
                if temp > 30:
                    cast += " Hot and mild, no storms expected under current pressure."
                elif 20 <= temp <= 30:
                    if dp < temp - 10:
                        cast += " Warm and mild, skies likely to stay clear."
                    elif dp > temp - 5:
                        cast += " Warm with moderate moisture and dew point, clouds possible, but rain unlikely."
                elif 10 <= temp < 20:
                    cast += " Pleasant and slightly humid - stable conditions."
                elif temp < 10:
                    if dp > temp - 5:
                        cast += " Cool and slightly damp - patchy mist or dew is possible overnight."
                    else:
                        cast += " Cool and dry - little weather activity expected."
            elif ah < 40:
                cast = "Dry conditions - fair weather expected."
                if temp > 30:
                    cast += " Hot and arid - clear skies dominate."
                elif 15 < temp <= 30:
                    cast += " Warm and dry - no precipitation expected."
                elif 5 < temp <= 15:
                    cast += " Cool and dry - crisp, clear weather likely."
                elif temp <= 5:
                    cast += " Cold and dry - snow very unlikely due to insufficient moisture."
        else:
            cast = "Unable to determine weather - sensor data unclear."
    elif indoor:
        print("\n**Indoor conditions**")
        if temp < 16:
            cast = "Indoor temperature is cold."
            if ah < 30:
                cast += " Air is also very dry - consider a humidifier and additional heating."
            elif ah > 60:
                cast += " It's cold and humid - may feel clammy or cause condensation."
            else:
                cast += " Dry but tolerable. Consider light heating for comfort."

        elif temp >= 16 and temp < 21:
            cast = "Indoor temperature is cool."
            if ah < 30:
                cast += " Air is dry - consider increasing humidity slightly."
            elif ah > 60:
                cast += " May feel cooler than it is due to higher humidity."
            else:
                cast += " Comfortable for most people, especially when active."

        elif temp >= 21 and temp < 25:
            cast = "Indoor temperature is comfortable."
            if ah < 30:
                cast += " Slightly dry air - may cause skin or throat dryness."
            elif ah > 60:
                cast += " May feel a bit muggy - ventilation could help."
            else:
                cast += " Ideal indoor climate."

        elif temp >= 25 and temp < 28:
            cast = "Indoor temperature is warm."
            if ah < 30:
                cast += " Dry heat - monitor for dehydration or static electricity."
            elif ah > 60:
                cast += " Humid and warm - could be uncomfortable without airflow."
            else:
                cast += " Warm but generally tolerable."

        elif temp >= 28:
            cast = "Indoor temperature is hot."
            if ah < 30:
                cast += " Air is hot and dry - risk of dehydration or discomfort."
            elif ah > 60:
                cast += " Air is hot and humid - high discomfort and potential for mold."
            else:
                cast += " Consider cooling - heat may cause fatigue."

        else:
            cast = "Unable to determine indoor comfort - values may be out of range."
    print(cast)
    if cast12m:
        print(f"\nFuture weather outlook? 12hr trend: {cast12}\nOutlook: {cast12m}")
        with open("12.txt", "a") as file:
            file.write(f"{cast12m}\n")
    if cast24m:
        print(f"\nFuture weather outlook? 24hr trend: {cast24}\nOutlook: {cast24m}")
        with open("24.txt", "a") as file:
            file.write(f"{cast24m}\n")
    if cast12m:
        print(f"\nFuture weather outlook? 48hr trend: {cast48}\nOutlook: {cast48m}")
        with open("48.txt", "a") as file:
            file.write(f"{cast48m}\n")
while True:
    if time >= stormchancewait:
        with open("time.txt", "w") as file:
            file.write("")
        stormchance()
        bplist = []
    elif timepass == cast24wait:
        stormchance()
    elif timepass == cast48wait:
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
        
    with open("timepass.txt", "r") as file:
        timepass = file.read()
    if not timepass:
        timepass = 1
    else:
        timepass = int(timepass.strip())
        timepass += 1
    with open("time.txt", "w") as file:
        file.write(str(time))
    with open("timepass.txt", "w") as file:
        file.write(str(timepass))
    print(time, timepass, stormchancewait, cast24wait, cast48wait)
    display.fill(0)
    display.text(str(f"{(1.8 * temp) + 32}F"), 0, 0, 1)
    display.text(str(f"{(1.8 * dp) + 32}F"), 0, 8, 1)
    display.text(str(ah) + "%", 0, 16, 1)
    display.text(str(bp) + "mb", 0, 24, 1)
    display.text(str(time) + "T", 0, 32, 1)
    display.text(str(timepass) + "TP", 0, 40, 1)
    if chance:
        display.text(str(chance) + " trend", 0, 48, 1)
    display.show()


    sleep(wait)