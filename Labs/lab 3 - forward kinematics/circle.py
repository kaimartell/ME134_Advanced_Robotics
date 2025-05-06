# circle.py
import time
import math
from XRPLib.differential_drive import DifferentialDrive


TRACK_WIDTH   = 20      #cm 
LAP_TIME      = 30.0    # seconds
LR_RATIO      = 0.5     # v_left / v_right
LOG_INTERVAL  = 0.1     
OUTPUT_CSV    = 'circle.csv'

#kinematic computations
R     = (TRACK_WIDTH/2) * (1 + LR_RATIO) / (1 - LR_RATIO)
v_ctr = (2 * math.pi * R) /  (1 * LAP_TIME)
v_r   = 2 * v_ctr / (1 + LR_RATIO)
v_l   = LR_RATIO * v_r

print(f"TRACK_WIDTH={TRACK_WIDTH} cm, R~={R:.2f} cm, v_l={v_l:.2f} cm/s, v_r={v_r:.2f} cm/s")

drivetrain = DifferentialDrive.get_default_differential_drive()
start_ms = time.ticks_ms()

# open csv
with open(OUTPUT_CSV, 'w') as f:
    # write header
    f.write('t_ms,left_speed,right_speed,left_enc_cm,right_enc_cm\n')
    
    # start the turn
    drivetrain.set_speed(v_l, v_r)
    
    # log until lap time expires
    while time.ticks_ms() - start_ms < int(LAP_TIME * 1000):
        t = time.ticks_ms() - start_ms
        le = drivetrain.get_left_encoder_position()
        re = drivetrain.get_right_encoder_position()
        # write one line immediately
        f.write(f"{t},{v_l:.3f},{v_r:.3f},{le:.3f},{re:.3f}\n")
        
        time.sleep(LOG_INTERVAL)
    
    drivetrain.stop()

# clear PID history
drivetrain.left_motor.speedController.clear_history()
drivetrain.right_motor.speedController.clear_history()

print("Done, data in", OUTPUT_CSV)
