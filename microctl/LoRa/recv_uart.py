from machine import Pin, SPI, UART
from sx1262 import SX1262
import time


uart_bus = 0
uart_tx = 12
uart_rx = 13

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

def init_uart():
    try:
        uart = UART(uart_bus, baudrate=9600, tx=Pin(uart_tx), rx=Pin(uart_rx))
        return uart
    except Exception as e:
        print(str(e))
        print("Uart failure.")
        return 0
    
def send_uart(msg):
    try:
        uart.write(f"{msg}\n")
        return 1
    except Exception as e:
        print(str(e))
        return 0

def print_batch(phrases):
    for item in phrases:
        print(item)
uart = init_uart()


if state != 0:
    if uart:
        send_uart(f"!LoRa initialization failed! Error: {state}")
    else:
        print(f"✗ LoRa initialization failed! Error: {state}")
else:
    if uart:
        send_uart(f"!LoRa initialized successfully!")
        send_uart(f"!Frequency: 915 MHz")
        send_uart(f"!Bandwidth: 125 kHz")
        send_uart(f"!Spreading Factor: 9")
        send_uart(f"!Coding Rate: 4/7")
        send_uart(f"!Listening for messages...")
    else:
        print("✓ LoRa initialized successfully!")
        print(f"Frequency: 915 MHz")
        print(f"Bandwidth: 125 kHz")
        print(f"Spreading Factor: 9")
        print(f"Coding Rate: 4/7")
        print("\nListening for messages...")



while True:
    try:
        
        data, state = lora.recv(timeout_en=True, timeout_ms=10000)
        
        if state == 0:
            try:
                message = data.decode()
                rssi = lora.getRSSI()
                snr = lora.getSNR()
                if uart:
                    send_uart(f"{message}#RSSI: {rssi}!SNR: {snr} dB")
                else:
                    print(f"{message}#RSSI: {rssi} SNR: {snr} dB")

            except:
                if uart:
                    send_uart(f"!Improper data:{data.hex()}")
                else:
                    print(f"!Improper data:{data.hex()}") 
        elif state == -6:  # Timeout
            pass
            
        elif state == -7:  # CRC error
            if uart:
                send_uart("!CRC mismatch - corrupted packet")
            else:
                print("!CRC mismatch - corrupted packet")
            
        else:
            if uart:
                send_uart(f"!Receive error: {state}")
            else:
                print(f"!Receive error: {state}")
        
    except KeyboardInterrupt:
        print("\n\nReceiver stopped")
        break
    except Exception as e:
        if uart:
            send_uart("!Error: {e}")
        else:
            print("!Error: {e}")
        time.sleep(1)
