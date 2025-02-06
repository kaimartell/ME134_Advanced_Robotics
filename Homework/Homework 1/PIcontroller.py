class PIController:
    def __init__(self, Kp, Ki, dt):
        self.Kp = Kp
        self.Ki = Ki
        self.dt = dt
        self.integral = 0
    
    def compute(self, error):
        self.integral += error * self.dt 
        u = self.Kp * error + self.Ki * self.integral
        return u
