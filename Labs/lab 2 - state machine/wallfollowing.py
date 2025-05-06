#wallfollowing.py
class WallFollower:
    def __init__(self, rangefinder, drivetrain, kp, base_speed, target_distance, window_size, debug=True, **kwargs):
        self.rangefinder = rangefinder
        self.drivetrain = drivetrain
        self.kp = kp
        self.base_speed = base_speed
        self.target_distance = target_distance
        self.window_size = window_size
        self.readings = []
        self.debug = debug

    def _get_valid_distance(self):
        d = self.rangefinder.distance()
        while d == 65535:
            d = self.rangefinder.distance()
        return d

    def _median_distance(self):
        # No akmath, use manual median sorting
        d = self._get_valid_distance()
        self.readings.append(d)
        if len(self.readings) > self.window_size:
            self.readings.pop(0)
        #median values
        sorted_vals = sorted(self.readings)
        mid = len(sorted_vals) // 2
        if len(sorted_vals) % 2:
            return sorted_vals[mid]
        else:
            return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0

    def step(self):
        dist = self._median_distance()
        error = self.target_distance - dist
        if self.debug:
            print(f"[WallFollower] dist: {dist}, error: {error}, correction: {self.kp * error}")
        corr = self.kp * error
        left = self.base_speed - corr
        right = self.base_speed + corr
        self.drivetrain.set_effort(left, right)