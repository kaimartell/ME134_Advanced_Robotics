#main.py
import time
from XRPLib.motor import Motor
from XRPLib.encoder import Encoder
from pid import PID

# Motor and encoder pin definitions.
RIGHT_MOTOR_A = 14
RIGHT_MOTOR_B = 15
LEFT_MOTOR_A = 6
LEFT_MOTOR_B = 7

# Robot and control parameters.
WHEEL_DIAMETER = 6  # cm
WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * 3.14159  # cm
SAMPLING_INTERVAL = 0.1  # seconds
TARGET_SPEED = 10  # desired forward speed in cm/s (always positive)

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

kp = 0.01
ki = 0.002
kd = 0.0005

print("Initializing PID controllers...")
right_motor_pid = PID(kp, ki, kd, TARGET_SPEED)
print("Right PID Initialized")
left_motor_pid = PID(kp, ki, kd, TARGET_SPEED)
print("Left PID Initialized")

print("Initialization complete.")

def counts_to_distance(counts, encoder):
    """
    Converts encoder counts to distance traveled (cm).
    """
    return (counts / encoder.resolution) * WHEEL_CIRCUMFERENCE

def calculate_velocity(previous_distance, current_distance, delta_time):
    """
    Calculates tangential velocity (cm/s) from the change in distance over time.
    """
    return (current_distance - previous_distance) / delta_time

def main():
    # Open a CSV file to log data.
    with open("log.csv", "w") as log_file:
        log_file.write("timestamp,right_velocity,left_velocity,right_effort,left_effort\n")

        start_time = time.time()
        previous_time = start_time
        previous_right_distance = 0.0
        previous_left_distance = 0.0

        # Run control loop for 10 seconds.
        while time.time() - start_time < 20:
            current_time = time.time()
            delta_time = current_time - previous_time

            if delta_time >= SAMPLING_INTERVAL:
                # Read encoder counts.
                right_counts = right_motor_encoder.get_position_counts()
                left_counts = left_motor_encoder.get_position_counts()

                # Convert counts to distance (cm).
                current_right_distance = counts_to_distance(right_counts, right_motor_encoder)
                current_left_distance = counts_to_distance(left_counts, left_motor_encoder)

                # Compute raw velocities in cm/s.
                raw_right_velocity = calculate_velocity(previous_right_distance, current_right_distance, delta_time)
                raw_left_velocity = calculate_velocity(previous_left_distance, current_left_distance, delta_time)
                
                # Effective forward speed:
                # - For the right motor: forward is when raw velocity is positive.
                # - For the left motor: forward is when raw velocity is negative (thus we invert it).
                effective_right_velocity = raw_right_velocity
                effective_left_velocity = -raw_left_velocity

                # Compute PID efforts.
                right_effort = right_motor_pid.calculate_effort(effective_right_velocity)
                left_effort = left_motor_pid.calculate_effort(effective_left_velocity)

                # Command motors.
                # Right motor: positive effort commands forward.
                # Left motor: negative effort commands forward.
                right_motor.set_effort(right_effort)
                left_motor.set_effort(-left_effort)

                # Log the data.
                log_line = f"{current_time},{raw_right_velocity},{raw_left_velocity},{right_effort},{-left_effort}\n"
                log_file.write(log_line)
                log_file.flush()
                print(log_line.strip())

                previous_time = current_time
                previous_right_distance = current_right_distance
                previous_left_distance = current_left_distance

            #time.sleep(0.01)

        # After 10 seconds, stop both motors.
        right_motor.set_effort(0)
        left_motor.set_effort(0)
        print("Time elapsed. Motors stopped.")

if __name__ == "__main__":
    main()
