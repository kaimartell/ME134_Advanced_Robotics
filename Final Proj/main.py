# main.py
import time
from robot import Robot

if __name__ == "__main__":
    xrp = Robot()
    try:
        while True:
            xrp.check_state()      # optional state polling
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("shutting down")
