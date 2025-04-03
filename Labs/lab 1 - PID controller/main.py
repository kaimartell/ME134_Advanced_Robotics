#main.py
import time
from XRPLib.motor import Motor
from XRPLib.encoder import Encoder
from pid import PID

# Motor and encoder pins
RIGHT_MOTOR_A = 14
RIGHT_MOTOR_B = 15
LEFT_MOTOR_A = 6
LEFT_MOTOR_B = 7

# Robot params
WHEEL_DIAMETER = 6  # cm
WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * 3.14159  # cm
SAMPLING_INTERVAL = 0.01  # seconds
TARGET_SPEED = 40  # cm/s

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


# PID Parameters
kp = 0.0025
ki = 0.02
kd = 0.0001

print("Initializing PID controllers...")
right_motor_pid = PID(kp, ki, kd, TARGET_SPEED)
print("Right PID Initialized")
left_motor_pid = PID(kp, ki, kd, TARGET_SPEED)
print("Left PID Initialized")

print("complete")

# Convert encoder counts to distance
def counts_to_distance(counts, encoder):
    return (counts / encoder.resolution) * WHEEL_CIRCUMFERENCE

# Calculate velocity from distance
def calculate_velocity(previous_distance, current_distance, delta_time):
    return (current_distance - previous_distance) / delta_time

def main():
    with open("log.csv", "w") as log_file:
        log_file.write("timestamp,right_velocity,left_velocity,right_effort,left_effort\n")

        previous_right_distance = 0.0
        previous_left_distance = 0.0

        start_time = time.ticks_ms()
        previous_time = start_time
        current_time = start_time
        while (current_time - start_time) / 1000 <= 20:
            
            current_time = time.ticks_ms()
  
            delta_time = (current_time - previous_time) / 1000
            if delta_time > SAMPLING_INTERVAL:
                # Read encoder counts
                right_counts = right_motor_encoder.get_position_counts()
                left_counts = left_motor_encoder.get_position_counts()

                # Convert counts to distance in cm
                current_right_distance = counts_to_distance(right_counts, right_motor_encoder)
                current_left_distance = counts_to_distance(left_counts, left_motor_encoder)

                # Compute raw velocities in cm/s
                raw_right_velocity = calculate_velocity(previous_right_distance, current_right_distance, delta_time)
                raw_left_velocity = calculate_velocity(previous_left_distance, current_left_distance, delta_time)
                
                # Effective forward speed
                # Flip left motor negative
                effective_right_velocity = raw_right_velocity
                effective_left_velocity = -raw_left_velocity

                # Compute PID effort
                right_effort, right_error = right_motor_pid.calculate_effort(effective_right_velocity)
                left_effort, left_error = left_motor_pid.calculate_effort(effective_left_velocity)

                # Set motor efforts
                right_motor.set_effort(right_effort)
                left_motor.set_effort(-left_effort)

                # Log data
                log_line = f"{current_time},{raw_right_velocity},{raw_left_velocity},{right_effort},{-left_effort},{right_error},{left_error}\n"
                log_file.write(log_line)
                log_file.flush()
                print(log_line.strip())

                previous_time = current_time
                previous_right_distance = current_right_distance
                previous_left_distance = current_left_distance

        # Stop motors
        right_motor.set_effort(0)
        left_motor.set_effort(0)
        print("Time elapsed. Motors stopped.")

if __name__ == "__main__":
    main()
