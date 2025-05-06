from XRPLib.encoder import Encoder
from XRPLib.motor import Motor
import time

"""
Almost all of this code was adopted from my main.py file
Slight modifications include not needing to control with PID
"""

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

effort = 1

def counts_to_distance(counts, encoder):
    return (counts / encoder.resolution) * WHEEL_CIRCUMFERENCE

def calculate_velocity(previous_distance, current_distance, delta_time):
    return (current_distance - previous_distance) / delta_time

def main():

    
    with open("efforttest.csv", "w") as log_file:
        log_file.write("timestamp,right_velocity,left_velocity,right_effort,left_effort\n")
        
        previous_right_distance = 0.0
        previous_left_distance = 0.0
        
        start_time = time.ticks_ms()
        previous_time = start_time
        current_time = start_time
        while (current_time - start_time) / 1000 <= 10:
            
            current_time = time.ticks_ms()
  
            delta_time = (current_time - previous_time) / 1000
            if delta_time > SAMPLING_INTERVAL:

                right_motor.set_effort(effort)
                left_motor.set_effort(-effort)        
                
                # Read encoder counts
                right_counts = right_motor_encoder.get_position_counts()
                left_counts = left_motor_encoder.get_position_counts()

                current_right_distance = counts_to_distance(right_counts, right_motor_encoder)
                current_left_distance = counts_to_distance(left_counts, left_motor_encoder)

                raw_right_velocity = calculate_velocity(previous_right_distance, current_right_distance, delta_time)
                raw_left_velocity = calculate_velocity(previous_left_distance, current_left_distance, delta_time)
                
                log_line = f"{current_time},{raw_right_velocity},{raw_left_velocity},{effort},{-effort}\n"
                log_file.write(log_line)
                log_file.flush()
                print(log_line.strip())
                
                previous_time = current_time
                previous_right_distance = current_right_distance
                previous_left_distance = current_left_distance
                
        right_motor.set_effort(0)
        left_motor.set_effort(0)

if __name__ == "__main__":
    main()