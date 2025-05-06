from XRPLib.differential_drive import DifferentialDrive
from machine import Timer
import time, math, gc, os
from XRPLib.board import Board
from XRPLib.defaults import *
drivetrain = DifferentialDrive.get_default_differential_drive()
import time
import math 
import random


sensor = reflectance.get_default_reflectance()

print("Waiting for start button...")
board.wait_for_button()  
print("Started! Press the button again to stop.")


base_effort = 0.3
KP = 1

drivetrain.set_effort(0,0)
while True:
    right = sensor.get_left()
    left = sensor.get_right()
    #print(f"Left: {left:.3f}, Right: {right:.3f}")

    error = right - 0.82
    #print("Error: ", error)


    drivetrain.set_effort(base_effort - KP * error, base_effort + KP * error)

    print(f"Left: {base_effort - KP * error:.3f}, Right: {base_effort + KP * error:.3f}")


    if board.is_button_pressed():  
        print("Stopped!")
        drivetrain.set_effort(0,0)
        board.wait_for_button()  
        break    

    time.sleep(0.1)


drivetrain.set_effort(0,0)