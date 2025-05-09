from XRPLib.differential_drive import DifferentialDrive
from machine import Timer
import time, math, gc, os
from XRPLib.board import Board
from XRPLib.defaults import *
drivetrain = DifferentialDrive.get_default_differential_drive()
import time
import math 
import random
from XRPLib.imu import IMU


imu = IMU.get_default_imu()
sensor = reflectance.get_default_reflectance()


Kp = 1
Ki = 0
Kd = 0.75

base_effort = 0.45

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.error_sum = 0
        self.error_delta = 0
        self.prev_error = 0
        self.effort = 0
        
    def update(self, error):
        
        
        P =  self.Kp * error 

        self.error_sum  += error
        I =  self.Ki * self.error_sum


        self.error_delta = (error - self.prev_error)
        D = self.Kd *  self.error_delta

        self.effort = P + I + D


        self.prev_error = error

        return self.effort

    
    def update_effort(self):

        right = sensor.get_left()
        left = sensor.get_right()

        error = left-right

        print(error)

        effort = self.update(error)

        drivetrain.set_effort(base_effort - effort, base_effort + effort)

        #print(f"Left: {base_effort - KP * error:.3f}, Right: {base_effort + KP * error:.3f}")



    def start_turn(self, clockwise=True):
        if clockwise:
            print("Turning clockwise...")
            drivetrain.set_effort(0.4,-0.4)
        else:
            print("Turning counter-clockwise...")
            drivetrain.set_effort(-0.4,0.4)

    def stop_motors(self):
        print("Motors stopped.")
        drivetrain.set_effort(0,0)


    def turn_90_degrees(self, imu, clockwise=True):
        target_angle = 85 #supoposed to be 90 but it was overturning
        direction = -1 if clockwise else 1 

        angle = 0.0
        last_time = time.ticks_ms()

        self.start_turn(clockwise)

        while abs(angle) < target_angle:
            rate_mdps = imu.get_gyro_z_rate() 
            rate_dps = rate_mdps / 1000.0

            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0  
            last_time = current_time

            angle += direction * rate_dps * dt

            time.sleep_ms(5) 

        self.stop_motors()
        print(f"Done turning. Final angle turned: {angle:.2f} degrees")


    def drive_straight_until_line(self, imu, target_heading, base_speed=0.4):
        kp = 0.01 

        right = sensor.get_left()
        left = sensor.get_right()

        

        while right < 0.9 and left < 0.9:
                
                current_heading = imu.get_yaw() 
                error = current_heading - target_heading


                #print(f"Right sensor: {right}, Left sensor: {left}")
                #print(f"Current heading: {current_heading} Target heading {target_heading}")
                #print(error)

                correction = kp * error

                left_speed = base_speed + correction
                right_speed = base_speed - correction

                drivetrain.set_effort(left_speed,right_speed)

                right = sensor.get_left()
                left = sensor.get_right()

                time.sleep(0.1)

        self.stop_motors()
        print("Line detected, stopped.")


"""drivetrain.set_effort(0,0)
print("Waiting for start button...")
board.wait_for_button()  # Wait for the button to start
print("Started! Press the button again to stop.")"""



"""#Turns right CW 90 degees
turn_90_degrees(imu, clockwise=True)

#Goes straight until it finds the line
target_heading = imu.get_yaw()
drive_straight_until_line(imu, target_heading)

#Moves foward just a bit
drivetrain.set_effort(0.3,0.3)
time.sleep(0.5)

#Turns CCW to sit up line
turn_90_degrees(imu, clockwise=False)"""


"""while True:

    if board.is_button_pressed():  
        print("Stopped!")
        drivetrain.set_effort(0,0)
        board.wait_for_button()  
        break    

    update_effort()

    time.sleep(0.1)

drivetrain.set_effort(0,0)"""