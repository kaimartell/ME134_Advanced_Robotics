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

drivetrain.set_effort(0,0)
while True:
    right = sensor.get_left()
    left = sensor.get_right()
    #print(f"Left: {left:.3f}, Right: {right:.3f}")

    if left > 0.8 and left < 0.9:
        drivetrain.set_effort(0.2,0.5)

        print("HARD")

    elif right > 0.8 and right <0.9:
        drivetrain.set_effort(0.5,0.2)  

        print("HARD")
    
    if left > 0.9:
        drivetrain.set_effort(0.2,0.4)

        print("soft")

    elif right > 0.9:
        drivetrain.set_effort(0.4,0.2)

        print("soft")

    else:
        drivetrain.set_effort(0.3,0.3)

        print("straight")


    if board.is_button_pressed():  
        print("Stopped!")
        drivetrain.set_effort(0,0)
        board.wait_for_button()  
        break    

    time.sleep(0.1)


drivetrain.set_effort(0,0)