import time
from XRPLib.rangefinder import Rangefinder

def main():
    ultrasonic = Rangefinder(26, 27)
    
    while True:
        distance = ultrasonic.distance()
        print(f"Distance: {distance} cm")
        time.sleep(0.1)