# forward_return.py
import time
from XRPLib.differential_drive import DifferentialDrive

drivetrain = DifferentialDrive.get_default_differential_drive()

# storage for: [t_ms, left_cmd_cmps, right_cmd_cmps, left_enc_cm, right_enc_cm]
log_data = []
start_time = time.ticks_ms()

def log(left_speed, right_speed):
    t = time.ticks_ms() - start_time
    le = drivetrain.get_left_encoder_position()
    re = drivetrain.get_right_encoder_position()
    log_data.append((t, left_speed, right_speed, le, re))

def save_csv():
    with open('forward_return.csv', 'w') as f:
        f.write('t_ms,left_speed,right_speed,left_enc_cm,right_enc_cm\n')
        for row in log_data:
            f.write(','.join(map(str, row)) + '\n')

def run():
    speed = 15  # cm/s

    #drive forward 10s
    t0 = time.ticks_ms()
    drivetrain.set_speed(speed, speed)
    while time.ticks_ms() - t0 < 10_000:
        log(speed, speed)
        time.sleep(0.05)
    drivetrain.stop()
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()
    time.sleep(1)

    print("turning")
    #turn 180
    log(0, 0)
    drivetrain.turn(180, max_effort=1, use_imu=False)
    log(0, 0)
    drivetrain.left_motor.speedController.clear_history()
    drivetrain.right_motor.speedController.clear_history()
    time.sleep(1)

    #drive back 10s
    print("driving back")
    t1 = time.ticks_ms()
    drivetrain.set_speed(speed, speed)
    while time.ticks_ms() - t1 < 10_000:
        log(speed, speed)
        time.sleep(0.05)
    drivetrain.stop()

    save_csv()

if __name__ == "__main__":
    run()
