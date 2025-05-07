#forwardkinematics.py
import math
import time
import gc
import uos
from XRPLib.defaults import drivetrain
from machine import Timer

#config init
DATA_INTERVAL_MS = 20       
FILENAME = "fk_log.csv"

#clear old log
if FILENAME in uos.listdir():
    uos.remove(FILENAME)
    print(f"{FILENAME} deleted.")
else:
    print(f"{FILENAME} does not exist.")

def init_log():
    with open(FILENAME, "w") as f:
        f.write("time_ms,x,y,theta\n")

init_log()

gc.collect()  #free RAM

dt = DATA_INTERVAL_MS / 1000.0  # sec

class PositionEstimation:
    def __init__(self, wheel_diam=6.0, track_width=15.5):
        self.dt = dt
        self.track = track_width
        self.rpm_to_cmps = math.pi * wheel_diam / 60.0
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0  # radians
        self._last_log = time.ticks_ms()

    def pose_update(self, t):
        try:
            # read wheel speeds, rpm to cm/s
            vl = drivetrain.left_motor.get_speed() * self.rpm_to_cmps
            vr = drivetrain.right_motor.get_speed() * self.rpm_to_cmps
            w = (vr - vl) / self.track

            # compute motion
            if abs(w) < 1e-6:
                # go straight
                v = 0.5 * (vl + vr)
                dx = v * math.cos(self.theta) * self.dt
                dy = v * math.sin(self.theta) * self.dt
                dtheta = 0.0
            else:
                # turn
                R = self.track * (vl + vr) / (2 * (vr - vl))
                dtheta = w * self.dt
                dx = -R * math.sin(self.theta) + R * math.sin(self.theta + dtheta)
                dy =  R * math.cos(self.theta) - R * math.cos(self.theta + dtheta)

            # Update state
            self.x += dx
            self.y += dy
            self.theta += dtheta

            # Log at intervals
            now = time.ticks_ms()
            if time.ticks_diff(now, self._last_log) >= DATA_INTERVAL_MS:
                with open(FILENAME, "a") as f:
                    f.write(f"{now},{self.x:.3f},{self.y:.3f},{self.theta:.4f}\n")
                self._last_log = now

        except ZeroDivisionError as zde:
            print("Pose update division error:", zde)
        except OSError as ose:
            print("Pose update I/O error:", ose)
        except Exception as e:
            print("Pose update error:", e)

kin = PositionEstimation()

drivetrain.reset_encoder_position()

# timer start
timer = Timer(-1) # negative timer for software
timer.init(period=DATA_INTERVAL_MS, mode=Timer.PERIODIC, callback=kin.pose_update)
print(f"Pose updates every {DATA_INTERVAL_MS}ms via Timer(-1)")

# motion sequence
sequence = [
    {"type": "speed", "left": 10, "right": 10, "duration": 3},
    {"type": "spin",  "rotations": 2, "effort": 1},
    {"type": "speed", "left": 30, "right": 30, "duration": 4},
]

for step in sequence:
    if step["type"] == "speed":
        print(f"[Motion] Speed L:{step['left']} R:{step['right']} cm/s for {step['duration']}s")
        drivetrain.set_speed(step["left"], step["right"])
        time.sleep(step["duration"])
        drivetrain.stop()
    elif step["type"] == "spin":
        rotations = step.get("rotations", 1)
        effort = step.get("effort", 1)
        start = kin.theta * 180 / math.pi
        target = start + rotations * 360
        print(f"[Motion] Spin from {start:.1f}° to {target:.1f}°")
        drivetrain.set_effort(effort, -effort)
        # wait for rotations
        while True:
            curr_deg = kin.theta * 180 / math.pi
            if abs(curr_deg - start) >= rotations * 360:
                break
            time.sleep(0.05)
        drivetrain.stop()
    # Rest
    time.sleep(1)

timer.deinit()
print("FK experiment complete, log in", FILENAME)
