#build a PID controller using motor encoder counts to reach a target speed

"""
To Do:
translate encoder counts into distances
translate distances into velocities, tweak with sampling frequencies
implement PID controller and tune PID parameters
"""

import time
from XRPLib.motor import Motor
from XRPLib.encoder import Encoder
from XRPLib.resetbot import reset_hard, reset_motors
from pid import PID
from mqtt import MQTTClient
import network


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

print("Initializing PID controllers...")
right_motor_pid = PID(0.1, 0.05, 0.01, TARGET_SPEED)
print("Right PID Initialized")
left_motor_pid = PID(0.1, 0.05, 0.01, TARGET_SPEED)
print("Left PID Initialized")

print("Initialization complete.")

time.sleep(1)

def main():
    try:
        mqtt_broker = 'broker.hivemq.com' 
        port = 1883
        topic_sub = 'ME134/Lab1'
        
        def callback(topic, msg):
            print(msg)

        client = MQTTClient('Kai', mqtt_broker , port, keepalive=0)
        client.connect()
        print('Connected to %s MQTT broker' % (mqtt_broker))    
        client.set_callback(callback) 
        client.subscribe(topic_sub.encode())  
        
        
        previous_time = time.time()
        previous_right_distance = 0
        previous_left_distance = 0

        while True:
            current_time = time.time()
            delta_time = current_time - previous_time

            if delta_time >= SAMPLING_INTERVAL:
                right_counts = right_motor_encoder.get_position_counts()
                left_counts = left_motor_encoder.get_position_counts()

                current_right_distance = counts_to_distance(right_counts, right_motor_encoder)
                current_left_distance = counts_to_distance(left_counts, left_motor_encoder)

                right_velocity = calculate_velocity(previous_right_distance, current_right_distance, delta_time)
                left_velocity = calculate_velocity(previous_left_distance, current_left_distance, delta_time)
                
                right_effort = abs(right_motor_pid.calculate_effort(right_velocity))
                left_effort = abs(left_motor_pid.calculate_effort(left_velocity)) * -1
                
                right_motor.set_effort(right_effort)
                left_motor.set_effort(left_effort)

                # Log velocities for debugging
                client.publish(topic_sub, f"{time.time()},{right_velocity},{left_velocity},{right_effort},{left_effort}")
                print(f"{time.time()},{right_velocity},{left_velocity},{right_effort},{left_effort}")
                
                previous_time = current_time
                previous_right_distance = current_right_distance
                previous_left_distance = current_left_distance

            time.sleep(0.01)


    except KeyboardInterrupt:
        right_motor_pid.reset()
        left_motor_pid.reset()
        reset_hard()
        print("Motors Reset and Program Terminated")
        
def init_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("Tufts_Robot", "")
    while wlan.ifconfig()[0] == '0.0.0.0':
        print('.', end=' ')
        time.sleep(1)
    print('wifi connected')
    return wlan.ifconfig()

    
def counts_to_distance(counts, motor):
    return ( counts / motor.resolution ) * WHEEL_CIRCUMFERENCE


def calculate_velocity(previous_distance, current_distance, delta_time):
    return (current_distance - previous_distance) / delta_time



if __name__ == "__main__":
    init_wifi()
    
    main()