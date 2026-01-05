from machine import Pin, SPI, I2C
from sx1262 import SX1262
import time
from bmp280 import BMP280
from ahtxx import AHT20

temp_mod = 0
delay = 1

SPI_BUS = 0
MISO_PIN = 0 
CS_PIN = 1
SCK_PIN = 2
MOSI_PIN = 3
BUSY_PIN = 6
RST_PIN = 7 
IRQ_PIN = 8

print("Initializing LoRa Transmitter...")

# Manual reset with longer delays
print("Resetting module...")
rst_pin = Pin(RST_PIN, Pin.OUT)
rst_pin.value(0)
time.sleep_ms(200)
rst_pin.value(1)
time.sleep_ms(200)

# Create LoRa instance
lora = SX1262(
    spi_bus=SPI_BUS,
    clk=SCK_PIN,
    mosi=MOSI_PIN,
    miso=MISO_PIN,
    cs=CS_PIN,
    irq=IRQ_PIN,
    rst=RST_PIN,
    gpio=BUSY_PIN
)

print("Attempting initialization...")
state = lora.begin(
    freq=915.0,
    bw=125.0,
    sf=9,
    cr=7,
    syncWord=0x12,
    power=14,
    currentLimit=60.0,
    preambleLength=8,
    implicit=False,
    crcOn=True,
    tcxoVoltage=0.0,  # No TCXO
    useRegulatorLDO=False
)

if state != 0:
    print(f"✗ LoRa initialization failed! Error: {state}")
else:
    print("✓ LoRa initialized successfully!")
    print(f"Frequency: 915 MHz")
    print(f"Bandwidth: 125 kHz")
    print(f"Spreading Factor: 9")
    print(f"Coding Rate: 4/7")

print("Initializing Temperature Module...")

def init_temp():
    time.sleep(delay)
    try:
        time.sleep_ms(1000)
        i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
        time.sleep_ms(1000)
        aht = AHT20(i2c)
        time.sleep_ms(1000)
        bmp = BMP280(i2c, addr=0x77)
        print("Moudle initialized")
        temp_mod = True
        return i2c, aht, bmp, temp_mod

    except Exception as e:
        temp_mod = False 
        print(str(e))
        print("Module not found")
        return 0, 0, 0, 0

def get():
    cur_temp = (aht.temperature + bmp.temperature) / 2
    cur_hum = aht.relative_humidity
    cur_pres = bmp.pressure / 100
    cur_temp = round(cur_temp, 2)
    cur_hum = round(cur_hum, 2)
    cur_pres = round(cur_pres, 2)
    return f"{str(cur_temp)} {str(cur_hum)} {str(cur_pres)}"

while True:
    try:
        if not temp_mod:
            i2c, aht, bmp, temp_mod = init_temp()
            if not i2c:
                if delay < 100:
                    delay += 2
            message = f"No module, waiting {delay} seconds"

        else:
            message = get()
        print(f"\nSending: {message}")
            
        sent_bytes, state = lora.send(message.encode())
            
        if state == 0:
              print(f"✓ Sent {sent_bytes} bytes successfully")
        else:
            print(f"✗ Send failed with error: {state}")
            
        time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTransmitter stopped")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)