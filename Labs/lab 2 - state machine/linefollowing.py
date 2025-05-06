# linefollowing.py
class LineFollower:
    def __init__(self, husky, drivetrain, kp, base_speed, target_x, debug=True, *args, **kwargs):
        self.husky = husky
        self.drivetrain = drivetrain
        self.kp = kp
        self.base_speed = base_speed
        self.target_x = target_x
        self.debug = debug

    def step(self):
        detections = self.husky.command_request_arrows()
        if detections:
            _, _, x2, _, _ = detections[0]
            error = x2 - self.target_x
            if self.debug:
                print(f"[LineFollower] x2: {x2}, error: {error}")
        else:
            error = 0
            if self.debug:
                print("[LineFollower] no line detected, driving straight")
        correction = self.kp * error
        left_effort = self.base_speed - correction
        right_effort = self.base_speed + correction
        self.drivetrain.set_effort(left_effort, right_effort)