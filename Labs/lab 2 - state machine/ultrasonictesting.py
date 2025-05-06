import time
from XRPLib.rangefinder import Rangefinder

def main():
    ultrasonic = Rangefinder(20, 21)
    
    while True:
        distance = ultrasonic.distance()
        print(f"Distance: {distance} cm")
        time.sleep(0.1)
        
if __name__ == "__main__":
    main()