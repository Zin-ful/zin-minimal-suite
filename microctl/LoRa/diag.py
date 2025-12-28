"""
LoRa SX1262 Diagnostic Test for RP2040 Zero
Tests SPI communication and pin connectivity
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

print("=== SX1262 Diagnostic Test ===\n")

# Test 1: GPIO Pin Setup
print("Test 1: Setting up GPIO pins...")
try:
    cs = Pin(CS_PIN, Pin.OUT, value=1)
    rst = Pin(RST_PIN, Pin.OUT, value=1)
    busy = Pin(BUSY_PIN, Pin.IN)
    irq = Pin(IRQ_PIN, Pin.IN)
    print("✓ GPIO pins configured")
except Exception as e:
    print(f"✗ GPIO setup failed: {e}")
    raise

# Test 2: SPI Setup
print("\nTest 2: Setting up SPI...")
try:
    spi = SPI(SPI_BUS, baudrate=2000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
    print("✓ SPI initialized")
    print(f"  SPI config: {spi}")
except Exception as e:
    print(f"✗ SPI setup failed: {e}")
    raise

# Test 3: BUSY Pin State
print("\nTest 3: Checking BUSY pin...")
busy_state = busy.value()
print(f"  BUSY pin state: {busy_state}")
if busy_state == 1:
    print("  ⚠ BUSY is HIGH - chip might be processing or not powered")
else:
    print("  ✓ BUSY is LOW - chip should be ready")

# Test 4: Hardware Reset
print("\nTest 4: Performing hardware reset...")
rst.value(0)
time.sleep_ms(10)
rst.value(1)
time.sleep_ms(10)
print("✓ Reset pulse sent")

# Wait for BUSY to go low
print("  Waiting for BUSY to go low...")
timeout = 0
while busy.value() and timeout < 100:
    time.sleep_ms(10)
    timeout += 1

if timeout >= 100:
    print("  ✗ BUSY didn't go low after reset!")
    print("  → Check power supply to SX1262")
    print("  → Verify BUSY pin connection")
else:
    print(f"  ✓ BUSY went low after {timeout*10}ms")

# Test 5: SPI Communication Test
print("\nTest 5: Testing SPI communication...")
cs.value(0)
time.sleep_ms(1)

# Try to read status (command 0xC0)
try:
    spi.write(b'\xC0')
    status = spi.read(1)
    cs.value(1)
    print(f"✓ SPI transaction completed")
    print(f"  Status byte: 0x{status[0]:02X}")
    
    if status[0] == 0x00 or status[0] == 0xFF:
        print("  ✗ Got 0x00 or 0xFF - no chip response!")
        print("  → Check MISO connection")
        print("  → Verify chip is powered (3.3V on VCC)")
        print("  → Check SCK and MOSI connections")
    else:
        print("  ✓ Chip is responding!")
        
except Exception as e:
    cs.value(1)
    print(f"✗ SPI communication failed: {e}")

# Test 6: Try initializing with library
print("\nTest 6: Attempting library initialization...")
try:
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
        crcOn=True
    )
    
    if state == 0:
        print("✓ LoRa initialized successfully!")
        print("\n=== ALL TESTS PASSED ===")
    else:
        print(f"✗ LoRa initialization failed with error: {state}")
        print("\nPossible issues:")
        print("  → Incorrect module type (check if it's really SX1262)")
        print("  → Insufficient power supply")
        print("  → Faulty module")
        
except Exception as e:
    print(f"✗ Library initialization failed: {e}")

print("\n=== Diagnostic Complete ===")