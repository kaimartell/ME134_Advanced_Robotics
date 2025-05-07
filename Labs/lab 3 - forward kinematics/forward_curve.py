# forward_curve.py
import time
from XRPLib.differential_drive import DifferentialDrive

drivetrain = DifferentialDrive.get_default_differential_drive()
log_data = []
start_time = time.ticks_ms()

def log(left_speed, right_speed):
    t = time.ticks_ms() - start_time
    le = drivetrain.get_left_encoder_position()
    re = drivetrain.get_right_encoder_position()
    log_data.append((t, left_speed, right_speed, le, re))

def save_csv():
    with open('forward_curve.csv', 'w') as f:
        f.write('t_ms,left_speed,right_speed,left_enc_cm,right_enc_cm\n')
        for row in log_data:
            f.write(','.join(map(str, row)) + '\n')

def run():
    speed = 15  # cm/s

    #straight
    t0 = time.ticks_ms()
    drivetrain.set_speed(speed, speed)
    while time.ticks_ms() - t0 < 5_000:
        log(speed, speed)
        time.sleep(0.05)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()
    time.sleep(10)

    #curve
    left_v = speed / 2
    right_v = speed
    t1 = time.ticks_ms()
    drivetrain.set_speed(left_v, right_v)
    while time.ticks_ms() - t1 < 5_000:
        log(left_v, right_v)
        time.sleep(0.05)
    drivetrain.stop()
    log(0, 0)

    save_csv()

if __name__ == "__main__":
    run()
