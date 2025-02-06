from XRPLib import board
from XRPLib.encoder import Encoder
from XRPLib.motor import Motor
import time


RIGHT_MOTOR_A = 14
RIGHT_MOTOR_B = 15

LEFT_MOTOR_A = 6
LEFT_MOTOR_B = 7

print("Reset")

WHEEL_DIAMETER = 6 #cm
WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * 3.14159 #cm
SAMPLING_INTERVAL = 0.1 #seconds
TARGET_SPEED = 10 #cm/s

print("here")

time.sleep(1)

print("Initializing encoders...")
right_motor_encoder = Encoder(1, 12, 13)
print("Right Encoder Initialized")
left_motor_encoder = Encoder(0, 4, 5)
print("Left Encoder Initialized")

time.sleep(1)

print("Initializing motors...")
right_motor = Motor(RIGHT_MOTOR_A, RIGHT_MOTOR_B)
print("Right Motor Initialized")
left_motor = Motor(LEFT_MOTOR_A, LEFT_MOTOR_B)
print("Left Motor Initialized")

time.sleep(1)


right_motor.set_effort(0)
left_motor.set_effort(0)

