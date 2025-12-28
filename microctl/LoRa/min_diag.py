"""
Minimal SX1262 initialization test
Tests each init step individually to find where it fails
"""

from machine import Pin, SPI
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

print("=== Minimal SX1262 Test ===\n")

# Setup pins
cs = Pin(CS_PIN, Pin.OUT, value=1)
rst = Pin(RST_PIN, Pin.OUT, value=1)
busy = Pin(BUSY_PIN, Pin.IN)
spi = SPI(SPI_BUS, baudrate=2000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))

def wait_busy(timeout_ms=1000):
    """Wait for BUSY to go low"""
    start = time.ticks_ms()
    while busy.value():
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            return False
        time.sleep_ms(1)
    return True

def spi_command(cmd, data=None):
    """Send SPI command and read status"""
    if not wait_busy(1000):
        print("  ✗ BUSY timeout before command")
        return None
    
    cs.value(0)
    time.sleep_us(1)
    
    # Send command
    spi.write(bytes([cmd]))
    
    # Send data if provided
    if data:
        status = bytearray(1)
        for byte in data:
            spi.write(bytes([byte]))
            # Read the response byte
            spi.readinto(status)
    else:
        status = spi.read(1)
    
    cs.value(1)
    time.sleep_us(1)
    
    if not wait_busy(1000):
        print("  ✗ BUSY timeout after command")
        return None
    
    return status[0] if status else None

# Reset chip
print("Step 1: Hardware reset...")
rst.value(0)
time.sleep_ms(10)
rst.value(1)
time.sleep_ms(10)
if wait_busy(1000):
    print("✓ Reset complete")
else:
    print("✗ Reset failed - BUSY stuck high")

# Get status
print("\nStep 2: Reading chip status...")
status = spi_command(0xC0)  # GET_STATUS
if status:
    print(f"✓ Status: 0x{status:02X}")
    mode = (status >> 4) & 0x07
    modes = {2: "STDBY_RC", 3: "STDBY_XOSC", 4: "FS", 5: "RX", 6: "TX"}
    print(f"  Mode: {modes.get(mode, 'UNKNOWN')}")
else:
    print("✗ Failed to read status")

# Set standby mode
print("\nStep 3: Setting standby mode (RC)...")
status = spi_command(0x80, [0x00])  # SET_STANDBY with RC
if status is not None:
    print(f"✓ Standby command sent, status: 0x{status:02X}")
else:
    print("✗ Standby command failed")

# Set packet type to LoRa
print("\nStep 4: Setting packet type to LoRa...")
status = spi_command(0x8A, [0x01])  # SET_PACKET_TYPE, 0x01=LoRa
if status is not None:
    print(f"✓ Packet type set, status: 0x{status:02X}")
    if (status & 0x0E) == 0x06:  # CMD_TIMEOUT
        print("  ⚠ Command timeout error!")
    elif (status & 0x0E) == 0x08:  # CMD_INVALID
        print("  ⚠ Invalid command error!")
    elif (status & 0x0E) == 0x0A:  # CMD_FAILED
        print("  ⚠ Command failed error!")
else:
    print("✗ Packet type command failed")

# Try setting frequency
print("\nStep 5: Setting RF frequency (915 MHz)...")
freq = int((915.0 * (1 << 25)) / 32.0)
freq_bytes = [
    (freq >> 24) & 0xFF,
    (freq >> 16) & 0xFF,
    (freq >> 8) & 0xFF,
    freq & 0xFF
]
status = spi_command(0x86, freq_bytes)  # SET_RF_FREQUENCY
if status is not None:
    print(f"✓ Frequency set, status: 0x{status:02X}")
else:
    print("✗ Frequency command failed")

# Read status again
print("\nStep 6: Final status check...")
status = spi_command(0xC0)
if status:
    print(f"✓ Status: 0x{status:02X}")
else:
    print("✗ Failed")

print("\n=== Now trying with library ===\n")

# Now try with the actual library
from sx1262 import SX1262

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

# Try without TCXO first (simpler)
print("Trying init without TCXO...")
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

print(f"\nResult: {state}")
if state == 0:
    print("✓✓✓ SUCCESS! ✓✓✓")
else:
    error_names = {
        -2: "ERR_CHIP_NOT_FOUND",
        -705: "ERR_SPI_CMD_TIMEOUT", 
        -706: "ERR_SPI_CMD_INVALID",
        -707: "ERR_SPI_CMD_FAILED"
    }
    print(f"✗ Error: {error_names.get(state, state)}")