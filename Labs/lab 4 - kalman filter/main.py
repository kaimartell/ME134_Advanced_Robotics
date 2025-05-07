# main.py
from XRPLib.defaults import drivetrain
from XRPLib.imu import IMU
import machine
from machine import Timer
import time, gc
from kalmanfilter import KalmanFilter

DT = 0.02  # seconds

gc.collect()  

def run_experiment(motion_sequence):
    #init
    kf = KalmanFilter(dt=DT)
    imu = IMU.get_default_imu()
    drivetrain.reset_encoder_position()
    imu.reset_yaw()

    # csv
    fname = "kalman_log.csv"
    f = open(fname, "w")
    f.write("time_ms,x_cm,y_cm,theta_rad,imu_yaw_deg\n")

    callback_count = {'count': 0}

    def timer_cb(t):
        callback_count['count'] += 1 # increment the count
        left_rpm = drivetrain.left_motor.get_speed()
        right_rpm = drivetrain.right_motor.get_speed()
        gyro_mdps = imu.get_gyro_z_rate()
        # Debug print every 50 calls
        if callback_count['count'] % 50 == 0: 
            print(f"[Timer #{callback_count['count']}] L:{left_rpm:.1f}rpm R:{right_rpm:.1f}rpm Gyro:{gyro_mdps:.1f}mdps")
        kf.step(left_rpm, right_rpm, gyro_mdps) # update KF
        ts = time.ticks_ms()
        f.write(f"{ts},{kf.x[0]:.3f},{kf.x[1]:.3f},{kf.x[2]:.4f},{imu.get_yaw():.2f}\n")

    try:
        kf_timer = Timer(1)
        print("[Timer] Using hardware Timer(1)")
    except (ValueError, TypeError):
        kf_timer = Timer(-1)
        print("[Timer] Timer(1) unavailable, using software Timer(-1)")
    kf_timer.init(freq=int(1/DT), callback=timer_cb)
    print(f"[Timer] KF callback running at {int(1/DT)}Hz")

    # motion seq
    for step in motion_sequence:
        typ = step.get("type", "speed")
        if typ == "speed":
            print(f"[Motion] Speed L:{step['left']} R:{step['right']} for {step['duration']}s")
            drivetrain.set_speed(step["left"], step["right"])
            time.sleep(step["duration"])
            drivetrain.stop()
        elif typ == "effort":
            print(f"[Motion] Effort L:{step['left']} R:{step['right']} for {step['duration']}s")
            drivetrain.set_effort(step["left"], step["right"])
            time.sleep(step["duration"])
            drivetrain.stop()
        elif typ == "spin":
            rotations = step.get("rotations", 1)
            effort = step.get("effort", 1)
            start_heading = imu.get_yaw()
            target = start_heading + rotations * 360
            print(f"[Motion] Spin start {start_heading:.2f}°, target {target:.2f}°")
            drivetrain.set_effort(effort, -effort)
            while True:
                current = imu.get_yaw()
                if abs(current - start_heading) >= rotations * 360:
                    break
                print(f"  spinning... curr={current:.2f}°, target={target:.2f}°")
                time.sleep(0.2)
            drivetrain.stop()
            print(f"[Motion] Spin complete at {imu.get_yaw():.2f}°")
        rest = step.get("rest", 1)
        print(f"[Rest] Sleeping {rest}s")
        time.sleep(rest)

    kf_timer.deinit()
    f.close()
    print("Data saved to", fname)

led = machine.Pin('LED', machine.Pin.OUT)
button = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)

if __name__ == "__main__":
    #led = machine.Pin('LED', machine.Pin.OUT)
    #button = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)
    sequence = [
        {"type": "speed", "left": 10, "right": 10, "duration": 3},
        {"type": "spin", "rotations": 2, "effort": 1},
        {"type": "speed", "left": 30, "right": 30, "duration": 4}
    ]
    run_experiment(sequence)
