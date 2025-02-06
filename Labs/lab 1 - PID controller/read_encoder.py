import time
from XRPLib.encoder import Encoder
from XRPLib.defaults import *

drivetrain.reset_encoder_position()

while True:
    
    left_wheel_position = drivetrain.get_left_encoder_position()
    print(f"Left Wheel Position: {left_wheel_position}")
    time.sleep(0.1)