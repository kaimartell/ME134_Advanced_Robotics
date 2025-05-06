from machine import I2C, Pin
import time
from Husky.huskylensPythonLibrary import HuskyLensLibrary

# Setup I2C
i2c = I2C(1, scl=Pin(19), sda=Pin(18))
print("I2C scan:", [hex(d) for d in i2c.scan()])

# init library
hl = HuskyLensLibrary("I2C")
hl.huskylensSer = i2c

#test
try:
    resp = hl.command_request_algorthim("ALGORITHM_LINE_TRACKING")
    print("Switched to Line Tracking:", resp)
except OSError as e:
    print("I2C write error:", e)

while True:
    try:
        data = hl.command_request_arrows()
        print("Arrow data:", data)
    except OSError as e:
        print("I2C read error:", e)
    time.sleep(0.5)
