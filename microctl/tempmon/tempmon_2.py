from machine import Pin, SoftI2C, PWM
from bmp280 import BMP280
from ahtxx import AHT20
from time import sleep
import ssd1306
import gc

screeni2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=400000)
display = ssd1306.SSD1306_I2C(128, 64, screeni2c)

temp_in = SoftI2C(sda=Pin(2), scl=Pin(3), freq=400000)
aht_in = AHT20(temp_in)
bmp_in = BMP280(temp_in, addr=0x77)

temp_out = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
aht_out = AHT20(temp_out)
bmp_out = BMP280(temp_out, addr=0x77)

fan_1 = Pin(9, Pin.OUT)
fan_2 = Pin(13, Pin.OUT)

light_1 = Pin(10, Pin.OUT)
light_2 = Pin(12, Pin.OUT)
light_3 = Pin(11, Pin.OUT)

fan_1.value(1)
fan_2.value(1)

light_1.value(0)
light_2.value(0)
light_3.value(0)

# Limit list size to prevent memory overflow
MAX_AVG_SAMPLES = 100

temp_avg_in = []
hum_avg_in = []

temp_avg_out = []
hum_avg_out = []

peak_temp_in = 0
peak_temp_out = 0
peak_hum_in = 0
peak_hum_out = 0

low_temp_in = 1000
low_temp_out = 1000
low_hum_in = 1000
low_hum_out = 1000

fan_on_threshhold = 20
alt_fan_on_threshhold = 20

wait = 1.0  # Changed from 0.0001 to 1 second
time = 0

pos = 0

touch_1 = Pin(29, Pin.IN, Pin.PULL_UP)
touch_2 = Pin(28, Pin.IN, Pin.PULL_UP)

def change_state(pins, state):
    i = 0
    while i <= len(pins) - 1:
        pins[i].value(state)
        print("turning to ", state)
        i += 1
        
def scrprint(string, x, y):
    display.text(string, x, y, 1)

def screrase(string, x, y):
    display.text(string, x, y, 0)

def scrclear():
    display.fill(0)
    display.show()

def get_stat(aht, bmp, cur_peak_temp, cur_peak_hum, cur_low_temp, cur_low_hum):
    
    peak_temp = 0
    peak_hum = 0
    low_temp = 0
    low_hum = 0
    cur_temp = (aht.temperature + bmp.temperature) / 2
    cur_hum = aht.relative_humidity    
    cur_pres = bmp.pressure / 100
    if cur_temp > float(cur_peak_temp):
        peak_temp = cur_temp
        peak_temp = round(peak_temp, 2)
    else:
        peak_temp = float(cur_peak_temp)
        
    
    if cur_hum > float(cur_peak_hum):
        peak_hum = cur_hum
        peak_hum = round(peak_hum, 2)
    else:
        peak_hum = float(cur_peak_hum)
    
    if cur_temp < float(cur_low_temp):
        low_temp = cur_temp
        low_temp = round(low_temp, 2)
    else:
        low_temp = float(cur_low_temp)
        
    
    if cur_hum < float(cur_low_hum):
        low_hum = cur_hum
        low_hum = round(low_hum, 2)
    else:
        low_hum = float(cur_low_hum)
        
    cur_temp = round(cur_temp, 2)
    cur_hum = round(cur_hum, 2)
    cur_pres = round(cur_pres, 2)
    return str(cur_temp), str(cur_hum), str(cur_pres), str(peak_temp), str(peak_hum), str(low_temp), str(low_hum)


def display_temperature():
    scrprint("Case Temp:", 0, 0)
    scrprint(temp_in + "C", 0, 8)
    scrprint(str((float(temp_in) * 1.8) + 32) + "F", 0, 16)
    scrprint("Room Temp:", 0, 24)
    scrprint(temp_out + "C", 0, 32)
    scrprint(str((float(temp_out) * 1.8) + 32) + "F", 0, 40)
    
def display_temp_avg():
    if len(temp_avg_in) > 0 and len(temp_avg_out) > 0:
        temp_trend_in = str(round(sum(temp_avg_in) / len(temp_avg_in), 2))
        temp_trend_out = str(round(sum(temp_avg_out) / len(temp_avg_out), 2))

        scrprint("Case Avg Temp:", 0, 0)
        scrprint(temp_trend_in + "C", 0, 8)
        scrprint(str(((float(temp_trend_in) * 1.8)+ 32)) + "F", 0, 16)
        scrprint("Room Avg Temp:", 0, 24)
        scrprint(temp_trend_out + "C", 0, 32)
        scrprint(str(((float(temp_trend_out) * 1.8) + 32)) + "F", 0, 40)
    else:
        scrprint("Collecting data...", 0, 0)
    
def display_humidity():
    scrprint("Case Humidity:", 0, 0)
    scrprint(hum_in + "%", 0, 8)
    scrprint("Room Humidity:", 0, 24)
    scrprint(hum_out + "%", 0, 32)
    
def display_hum_avg():
    if len(hum_avg_in) > 0 and len(hum_avg_out) > 0:
        hum_trend_in = str(round(sum(hum_avg_in) / len(hum_avg_in), 2))
        hum_trend_out = str(round(sum(hum_avg_out) / len(hum_avg_out), 2))

        scrprint("Case Avg Hum:", 0, 0)
        scrprint(hum_trend_in + "%", 0, 8)
        scrprint("Room Avg Hum:", 0, 24)
        scrprint(hum_trend_out + "%", 0, 32)
    else:
        scrprint("Collecting data...", 0, 0)

def display_peak_temp():
    scrprint("Peak Temps:", 0, 0)
    scrprint(peak_temp_in + "C", 0, 8)
    scrprint(peak_temp_out + "C", 0, 16)
    scrprint("Low Temps:", 0, 24)
    scrprint(low_temp_in + "C", 0, 32)
    scrprint(low_temp_out + "C", 0, 40)
    
def display_peak_hum():
    scrprint("Peak Hum:", 0, 0)
    scrprint(peak_hum_in + "%", 0, 8)
    scrprint(peak_hum_out + "%", 0, 16)
    scrprint("Low Hum:", 0, 24)
    scrprint(low_hum_in + "%", 0, 32)
    scrprint(low_hum_out + "%", 0, 40)

def display_pressure():
    scrprint("Pressure In:", 0, 0)
    scrprint(pres_in + "mb", 0, 8)
    scrprint("Pressure Out:", 0, 16)
    scrprint(pres_out + "mb", 0, 24)
    
def display_utility():
    unallocated_mem = str(gc.mem_free() // 1024)
    allocated_mem = str(gc.mem_alloc() // 1024)
    scrprint("Mem Free:", 0, 0)
    scrprint(unallocated_mem + "Kb", 0, 8)
    scrprint("Mem Used:", 0, 16)
    scrprint(allocated_mem + "Kb", 0, 24)
    scrprint("List Sizes:", 0, 32)
    scrprint(f"T: {len(temp_avg_out) + len(temp_avg_in)} H: {len(hum_avg_out) + len(hum_avg_in)}", 0, 40)

menu = [display_temperature, display_temp_avg, display_peak_temp, display_humidity, display_hum_avg, display_peak_hum, display_pressure, display_utility]

# Startup sequence
change_state((fan_1, fan_2), 1)
change_state((light_1, light_2, light_3), 0)
sleep(1)
change_state((fan_1,), 0)
change_state((light_1,), 1)
sleep(1)
change_state((fan_1,), 1)
change_state((light_1,), 0)
sleep(1)
change_state((fan_2,), 0)
change_state((light_2,), 1)
sleep(1)
change_state((fan_2,), 1)
change_state((light_2,), 0)
sleep(1)
change_state((fan_1, fan_2), 0)
change_state((light_1, light_2, light_3), 1)
sleep(1)
change_state((fan_1, fan_2), 1)
change_state((light_1, light_2, light_3), 0)

while True:
    temp_in, hum_in, pres_in, peak_temp_in, peak_hum_in, low_temp_in, low_hum_in = get_stat(aht_in, bmp_in, float(peak_temp_in), float(peak_hum_in), float(low_temp_in), float(low_hum_in))
    
    # Limit list size to prevent memory overflow
    temp_avg_in.append(float(temp_in))
    if len(temp_avg_in) > MAX_AVG_SAMPLES:
        temp_avg_in.pop(0)
        
    hum_avg_in.append(float(hum_in))
    if len(hum_avg_in) > MAX_AVG_SAMPLES:
        hum_avg_in.pop(0)
    
    temp_out, hum_out, pres_out, peak_temp_out, peak_hum_out, low_temp_out, low_hum_out = get_stat(aht_out, bmp_out, float(peak_temp_out), float(peak_hum_out), float(low_temp_out), float(low_hum_out))
    
    temp_avg_out.append(float(temp_out))
    if len(temp_avg_out) > MAX_AVG_SAMPLES:
        temp_avg_out.pop(0)
        
    hum_avg_out.append(float(hum_out))
    if len(hum_avg_out) > MAX_AVG_SAMPLES:
        hum_avg_out.pop(0)
    
    display.fill(0)
    menu[pos]()
    display.show()
    
    if float(temp_in) >= fan_on_threshhold:
        change_state((fan_1,), 0)
        change_state((light_1,), 1)
        print("turning fan one on")
    elif float(temp_in) <= fan_on_threshhold and fan_1.value() == 0:
        change_state((fan_1,), 1)
        change_state((light_1,), 0)
        print("turning fan one off")

    
    if float(temp_in) >= alt_fan_on_threshhold:
        change_state((fan_2,), 0)
        change_state((light_2,), 1)
        print("turning fan two on")
    elif float(temp_in) <= alt_fan_on_threshhold and fan_2.value() == 0:
        change_state((fan_2,), 1)
        change_state((light_2,), 0)
        print("turning fan two off")

    
    if touch_1.value() == 1:
        pos += 1
        if pos > len(menu) - 1:
            pos = len(menu) - 1
            
    print(time)    
    time += 1
    
    # Run garbage collection periodically
    if time % 10 == 0:
        gc.collect()
        print(f"Memory free: {gc.mem_free()}")

    sleep(wait)
