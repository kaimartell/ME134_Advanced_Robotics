# kalmanfilter.py
import math

class KalmanFilter:
    """
    Three-state Kalman filter for (x, y, θ) fusion of differential-drive kinematics and gyro.
    θ in radians.
    """
    def __init__(self, wheel_diam=6.0, track_width=15.5, dt=0.02):
        self.dt = dt
        # robot params
        self.track_width = track_width
        self.rpm_to_cmps = (math.pi * wheel_diam) / 60.0

        # Initial state x
        self.x = [0.0, 0.0, 0.0]
        # Covariance P
        self.P = [[0.1, 0.0, 0.0],
                  [0.0, 0.1, 0.0],
                  [0.0, 0.0, 0.1]]
        # Process noise Q
        self.Q = [[0.01, 0.0, 0.0],
                  [0.0, 0.01, 0.0],
                  [0.0, 0.0, 0.01]]
        # measurement noise R
        self.R_theta = 0.01

    def predict(self, left_rpm, right_rpm):
        """
        Prediction step using wheel encoder speeds (RPM).
        """
        vl = left_rpm * self.rpm_to_cmps
        vr = right_rpm * self.rpm_to_cmps
        w = (vr - vl) / self.track_width

        if abs(w) < 1e-6:
            v = 0.5 * (vl + vr)
            dx = v * math.cos(self.x[2]) * self.dt
            dy = v * math.sin(self.x[2]) * self.dt
            dtheta = 0.0
        else:
            R = self.track_width * (vl + vr) / (2 * (vr - vl))
            theta = self.x[2]
            dtheta = w * self.dt
            dx = -R * math.sin(theta) + R * math.sin(theta + dtheta)
            dy =  R * math.cos(theta) - R * math.cos(theta + dtheta)

        # Update state
        self.x[0] += dx
        self.x[1] += dy
        self.x[2] += dtheta

        # Covariance update
        for i in range(3):
            for j in range(3):
                self.P[i][j] += self.Q[i][j]

    def update(self, gyro_mdps): # update step using gyro
        gyro_deg_s = gyro_mdps / 1000.0 # convert to deg/s
        gyro_rad_s = gyro_deg_s * (math.pi / 180.0) # convert to rad/s
        z_delta = gyro_rad_s * self.dt
        z = self.x[2] + z_delta

        P22 = self.P[2][2]
        K = P22 / (P22 + self.R_theta)

        self.x[2] = self.x[2] + K * (z - self.x[2])
        self.P[2][2] = (1 - K) * P22

    def step(self, left_rpm, right_rpm, gyro_mdps): # main step
        self.predict(left_rpm, right_rpm)
        self.update(gyro_mdps)