"""
LoRa Receiver for RP2040 Zero + SX1262
Upload this to Device 2
"""

from machine import Pin, SPI
from sx1262 import SX1262
import time

# Your pin configuration
SPI_BUS = 0
MISO_PIN = 0 
CS_PIN = 1
SCK_PIN = 2
MOSI_PIN = 3
BUSY_PIN = 6
RST_PIN = 7 
IRQ_PIN = 8

print("Initializing LoRa Receiver...")

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

# Initialize with working settings
state = lora.begin(
    freq=915.0,      # Must match transmitter!
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
    print("\nListening for messages...")

# Receive loop
while True:
    try:
        # Receive with 5 second timeout
        data, state = lora.recv(timeout_en=True, timeout_ms=5000)
        
        if state == 0:  # Success
            try:
                message = data.decode()
                rssi = lora.getRSSI()
                snr = lora.getSNR()
                print(f"\n✓ Received: {message}")
                print(f"  RSSI: {rssi} dBm")
                print(f"  SNR: {snr} dB")
                print(f"  Length: {len(data)} bytes")
            except:
                print(f"\n✓ Received {len(data)} bytes (not UTF-8)")
                print(f"  Raw: {data.hex()}")
                
        elif state == -6:  # Timeout
            print(".", end="")
            
        elif state == -7:  # CRC error
            print("\n✗ CRC mismatch - corrupted packet")
            
        else:
            print(f"\n✗ Receive error: {state}")
        
    except KeyboardInterrupt:
        print("\n\nReceiver stopped")
        break
    except Exception as e:
        print(f"\nError: {e}")
        time.sleep(1)