from machine import Pin, I2C
from bmp280 import BMP280
from ahtxx import AHT20
from time import sleep
import ssd1306
import gc

screeni2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
display = ssd1306.SSD1306_I2C(128, 64, screeni2c)
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
aht = AHT20(i2c)
bmp = BMP280(i2c, addr=0x77)
temp_avg = []
hum_avg = []
peak_temp = 0
peak_hum = 0
wait = 2
time = 0

def scrprint(string, x, y):
    display.text(string, x, y, 1)

def screrase(string, x, y):
    display.text(string, x, y, 0)

def scrclear():
    display.fill(0)
    display.show()

def get_stat():
    peak = 0
    peakh = 0
    temp_avg.append(aht.temperature)
    temp_avg.append(bmp.temperature)
    hum_avg.append(aht.relative_humidity)
    cur_temp = (aht.temperature + bmp.temperature) / 2
    cur_hum = aht.relative_humidity    
    cur_pres = bmp.pressure / 100
    if cur_temp > float(peak_temp):
        peak = cur_temp
        peak = round(peak, 2)
    else:
        peak = float(peak_temp)
    if cur_hum > float(peak_hum):
        peakh = cur_hum
        peakh = round(peakh, 2)
    else:
        peakh = float(peak_hum)
    cur_temp = round(cur_temp, 2)
    cur_hum = round(cur_hum, 2)
    cur_pres = round(cur_pres, 2)
    return str(cur_temp), str(cur_hum), str(cur_pres), str(peak), str(peakh)
    

while True:
    cur_temp, cur_hum, cur_pres, peak_temp, peak_hum = get_stat()
    
    temp_trend = str(round(sum(temp_avg) / len(temp_avg), 2))
    hum_trend = str(round(sum(hum_avg) / len(hum_avg), 2))
    unallocated_mem = str(gc.mem_free() // 1024)
    allocated_mem = str(gc.mem_alloc() // 1024)
    
    scrprint(cur_temp + "C & " + cur_hum + "%", 0, 0)
    scrprint("A " + temp_trend + "C " + hum_trend + "%", 0, 10)
    scrprint("P " + peak_temp + "C " + peak_hum + "%", 0, 20)

    scrprint(cur_pres + "mb", 0, 30)
    
    scrprint(f"mm {allocated_mem}k/{unallocated_mem}k u/f" , 0, 40)
    display.show()    
    sleep(wait)
    screrase(cur_temp + "C & " + cur_hum + "%", 0, 0)
    screrase("A " + temp_trend + "C " + hum_trend + "%", 0, 10)
    screrase("P " + peak_temp + "C " + peak_hum + "%", 0, 20)

    screrase(cur_pres + "mb", 0, 30)
    
    screrase(f"mm {allocated_mem}k/{unallocated_mem}k u/f" , 0, 40)
    
    time += wait
    if len(temp_avg) + len(hum_avg) > 1500:
        del temp_avg
        del hum_avg
        gc.collect()
        temp_avg = []
        hum_avg = []
        time = 0
    elif gc.mem_free() < 12000:
        gc.collect()
