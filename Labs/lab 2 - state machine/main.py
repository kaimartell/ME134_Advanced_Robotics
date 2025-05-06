# main.py
import time
from XRPLib.defaults import drivetrain, rangefinder
from Husky.huskylensPythonLibrary import HuskyLensLibrary as Husky
from randomwalk import RandomWalk
from linefollowing import LineFollower
from wallfollowing import WallFollower

# State labels
RANDOM = 'RANDOM'
LINE = 'LINE'
WALL = 'WALL'

class LineWallFSM:
    def __init__(self, debug=True):
        self.state = RANDOM
        self.debug = debug
        self.husky = Husky('I2C')
        self.husky.line_tracking_mode()
        self.random_walker = RandomWalk(drivetrain, debug)
        self.line_follower = LineFollower(self.husky, drivetrain, -0.002, 0.4, 160, debug)
        self.wall_follower = WallFollower(rangefinder, drivetrain, 0.03, 0.35, 15, 5, debug)
        self.behaviors = {
            RANDOM: self.random_walker,
            LINE: self.line_follower,
            WALL: self.wall_follower
        }

    def _detect_line(self):
        return bool(self.husky.command_request_arrows())

    def _detect_wall(self):
        return self.wall_follower._median_distance() < 40

    def _transition(self):
        prev = self.state
        if self.state == RANDOM:
            if self._detect_wall():
                self.state = WALL
            elif self._detect_line():
                self.state = LINE
        elif self.state == LINE:
            if not self._detect_line():
                self.state = WALL if self._detect_wall() else RANDOM
        elif self.state == WALL:
                # Prioritize line if detected, even when still near a wall
                if self._detect_line():
                    self.state = LINE
                elif not self._detect_wall():
                    self.state = RANDOM
        if self.debug and prev != self.state:
            print(f"Transition: {prev} -> {self.state}")

    def run(self):
        try:
            while True:
                if self.debug:
                    print(f"Current state: {self.state}")
                self._transition()
                self.behaviors[self.state].step()
                time.sleep(0.05)
        except KeyboardInterrupt:
            drivetrain.stop()
            if self.debug:
                print("Stopped")

if __name__ == '__main__':
    LineWallFSM().run()
