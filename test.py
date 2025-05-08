from XRPLib.differential_drive import DifferentialDrive
from machine import Timer
import time, math, gc, os
from XRPLib.board import Board
from XRPLib.defaults import *
drivetrain = DifferentialDrive.get_default_differential_drive()


# MOTOR AND IMU SETUP
left_motor = EncodedMotor.get_default_encoded_motor(index=1)
right_motor = EncodedMotor.get_default_encoded_motor(index=2)
imu = IMU.get_default_imu()
hardware_timer_period = 0.1  # s
data = []  # Temporary storage for other data


FK_x_pos = []
FK_y_pos = []
kf_x_pos = []
kf_y_pos = []

class PositionEstimation:
    def __init__(self):

        self.x = self.y = self.theta = 0
        self.kf_x = self.kf_y = self.kf_theta = 0
        self.prev_kf_theta = 0
        self.w = self.w_kf = 0

        self.track_width = 15.5
        self.wheel_diameter = 6
        self.RPMtoCMPS = (math.pi* self.wheel_diameter) / 60
        self.CMPStoRPM = 60 / (math.pi*self.wheel_diameter)





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


    def k_filt(self):

        self.prev_kf_theta = self.kf_theta


        #prediction
        
        self.w_kf = imu.get_gyro_z_rate() * (math.pi / 180000)

        theta_z = self.kf_theta + self.w_kf * hardware_timer_period
        theta_x = self.prev_kf_theta + self.w * hardware_timer_period
        innovation = (theta_z-theta_x)
        self.P = self.matrix_add(self.P,self.Q)


        # Update step
        P_theta = self.P[2][2]
        R_theta = self.R[2][2]
        K = P_theta/(P_theta + R_theta)

        self.kf_theta = theta_x + K*innovation
        self.P[2][2] = (1-K)*self.P[2][2]
  

    def update_both(self):

        
        #Move to seperate funciton
        
        left_speed = left_motor.get_speed() * self.RPM_TO_CMPS
        right_speed = right_motor.get_speed() * self.RPM_TO_CMPS 

        self.w = (right_speed - left_speed) / self.TRACK_WIDTH_CM

        if self.w == 0:
            V = 0.5 * (left_speed + right_speed)
            self.x = self.x + V * math.cos(self.theta) * hardware_timer_period
            self.y = self.y + V * math.sin (self.theta) * hardware_timer_period

        else:
            R_val = self.track_width * (right_speed + left_speed) / (2 * (right_speed - left_speed))
            self.x = self.x + -R_val * math.sin(self.theta) + R_val * math.sin(self.theta + self.w * hardware_timer_period)
            self.y = self.y + R_val * math.cos(self.theta) - R_val * math.cos(self.theta + self.w * hardware_timer_period)
            #self.theta = self.theta + self.w * hardware_timer_period

        
        self.kalman_filter()


        if self.w == 0:
            V = 0.5 * (left_speed + right_speed)
            self.kf_x = self.kf_x + V * math.cos(self.prev_kf_theta) * hardware_timer_period
            self.kf_y = self.kf_y + V * math.sin (self.prev_kf_theta) * hardware_timer_period

        else:
            R_val = self.track_width * (right_speed + left_speed) / (2 * (right_speed - left_speed))
            self.kf_x = self.kf_x + -R_val * math.sin(self.prev_kf_theta) + R_val * math.sin(self.kf_theta)
            self.kf_y = self.kf_y + R_val * math.cos(self.prev_kf_theta) - R_val * math.cos(self.kf_theta)
            #self.theta = self.theta + self.w * hardware_timer_period

        FK_x_pos.append(self.x)
        FK_y_pos.append(self.y)
        kf_x_pos.append(self.kf_x)
        kf_y_pos.append(self.kf_y)

    
kinematics = PositionEstimation()
    
def execute_trajectory():

    motion_sequence = [

        (0, 0, 1), (20, 20, 5), (-100, 100, 5), (20, 20, 4), (0, 0, 0)
    ]

    for left, right, duration in motion_sequence:
        kinematics.set_motor_target_speeds(left, right)
        time.sleep(duration)


    # def run_system(self):
    #     timer = Timer()
    #     self.display = False
    #     board.wait_for_button()

    #     timer.init(period=int(hardware_timer_period * 1000),
    #        mode=Timer.PERIODIC, 
    #        callback=lambda t: kinematics.update_coord())



     

