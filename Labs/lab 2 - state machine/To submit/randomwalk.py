#randomwalk.py

import random
import time

class RandomWalk:
    def __init__(self, drivetrain, debug=True):
        self.drivetrain = drivetrain
        self.base_speed = 0.4
        self.debug = debug

    def step(self):
        turn_rate = random.uniform(-0.1, 0.1)
        print("speed: ", self.base_speed)
        if self.debug:
            print(f'[RandomWalker] turn_rate: {turn_rate}')
        self.drivetrain.arcade(self.base_speed, turn_rate)
        time.sleep(0.2)