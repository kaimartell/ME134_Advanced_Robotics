from XRPLib.differential_drive import DifferentialDrive
from machine import Timer
import time, math, gc, os
from XRPLib.board import Board
from XRPLib.defaults import *
drivetrain = DifferentialDrive.get_default_differential_drive()


#MATRIX OPERATIONS

#Motor and IMU setup
left_motor = EncodedMotor.get_default_encoded_motor(index=1)
right_motor = EncodedMotor.get_default_encoded_motor(index=2)
imu = IMU.get_default_imu()
hardware_timer_period = 0.1 #s
data = [] # temp. storage


### NOT SURE IF THIS IS RIGHT
DT = 0.02
data_interval = 20 #ms

#Matrix operations



#INITIALIZING VARIABLES

class PositionEstimation:

    

    def __init__(self):
        # State estimates
        self.x = self.y = self.theta = 0.0 #X(k, k) - state of robot
        self.x_x = self.x_y = self.x_theta = 0.0 #X(k,k-1) - intermediate result from model
        self.z_x = self.z_y = self.z_theta = 0.0 #z - additional sensor measurement
        self.wheel_diam = 6 #cm
        self.TRACK_WIDTH_CM = 15.5 #cm
        self.RPM_TO_CMPS = (math.pi * self.wheel_diam) / 60     # Covert from RPM to cm/s
        self.CMPS_TO_RPM = 60 / (math.pi * self.wheel_diam)     # Covert from cm/s to RPM
        self.innovation = 0
        self.K_theta = 0



        self.P = [
            [0.1, 0.0, 0.0],
            [0.0, 0.1, 0.0],
            [0.0, 0.0, 0.1]
        ]

        self.Q = [
            [0.01, 0.0, 0.0],
            [0.0, 0.01, 0.0],
            [0.0, 0.0, 0.01]
        ]

        self.R = [
            [0.05, 0.0, 0.0],
            [0.0, 0.05, 0.0],
            [0.0, 0.0, 0.01]
        ]

    def matrix_add(self,A,B):
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    def invert_diagonal_matrix(self,M):
        return [[1.0 / M[i][j] if i == j and M[i][j] != 0 else 0.0 for j in range(len(M))] for i in range(len(M))]

    def matrix_multiply(self,A,B):
        return [
            [sum (A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
            for i in range (len(A))
        ]    


        # Covariance matricies


    #PREDICTION STEP


    def FK(self):
        left_speed = left_motor.get_speed() * self.RPM_TO_CMPS
        right_speed = right_motor.get_speed() * self.RPM_TO_CMPS
        w = (right_speed - left_speed) / self.TRACK_WIDTH_CM

        if w == 0:
            V = 0.5 * (left_speed + right_speed)
            self.x_x = self.x_x + V * math.cos(self.x_theta) * DT
            self.x_y = self.x_y + V * math.sin (self.x_theta) * DT

        else:
            R_val = self.TRACK_WIDTH_CM * (right_speed + left_speed) / (2 * (right_speed - left_speed))
            self.x_x = self.x_x + -R_val * math.sin(self.x_theta) + R_val * math.sin(self.x_theta + w * DT)
            self.x_y = self.x_y + R_val * math.cos(self.x_theta) - R_val * math.cos(self.x_theta + w * DT)
            self.x_theta = self.x_theta + w * DT

        
        #print(self.x_x,self.x_y,self.x_theta)


    
    def covariance_matrix(self):
        self.P = self.matrix_add(self.P, self.Q)




    def prediction_step(self):

        self.FK()
        self.covariance_matrix()


    def gyro_readings(self):
        gyro_z_rad_per_s = imu.get_gyro_z_rate() * (math.pi / 180000)
        self.z_theta += gyro_z_rad_per_s * DT

    
    def kalman_gain(self):

        self.gyro_readings()

        self.innovation = self.z_theta - self.x_theta
        P_theta = self.P[2][2]
        R_theta = self.R[2][2]
        self.K_theta = P_theta / (P_theta + R_theta)

    
    def update_state_estimate(self):

        self.theta = self.x_theta + self.K_theta * self.innovation
        self.x_theta = self.theta

        #self.FK()

        #self.x = self.x_x
        #self.y = self.x_y
        #self.theta = self.x_theta

        data.append([self.x,self.y,self.theta])

    def update_convariance_matrix(self):

        self.P[2][2] = (1 - self.K_theta) * self.P[2][2]

    def update_step(self):
        

        self.kalman_gain()
        self.update_state_estimate()
        self.update_convariance_matrix()

        

        #print(self.P)

    
    def set_motor_target_speeds (self, left_cmps, right_cmps):
        left_motor.set_speed(left_cmps * self.CMPS_TO_RPM)
        right_motor.set_speed(right_cmps * self.CMPS_TO_RPM)

    
    def K_filter(self):

        self.prediction_step()
        self.update_step()




kinematics = PositionEstimation()

def execute_trajectory():

    motion_sequence = [

        (0, 0, 1), (20, 20, 5), (-100, 100, 5), (20, 20, 4), (0, 0, 0)
    ]

    for left, right, duration in motion_sequence:
        kinematics.set_motor_target_speeds(left, right)
        time.sleep(duration)

timer = Timer()
timer.init(period=int (DT * 1000),
    mode=Timer. PERIODIC,
    callback=lambda t: (
        kinematics.K_filter(),
        
    )
)

execute_trajectory()
print(data)
           









