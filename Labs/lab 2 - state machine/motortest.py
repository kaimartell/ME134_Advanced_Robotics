# motor_test.py

import time
from XRPLib.defaults import DifferentialDrive

drive = DifferentialDrive.get_default_differential_drive()

print("Spinning LEFT motor alone at 20cm/s for 3s")
drive.set_speed(20, 0)
time.sleep(3)
drive.set_speed(0, 0)
time.sleep(1)

print("Spinning RIGHT motor alone at 20cm/s for 3s")
drive.set_speed(0, 20)
time.sleep(3)
drive.set_speed(0, 0)
