# robot.py
from Husky.huskylensPythonLibrary import HuskyLensLibrary
from MQTT.mqtt import MQTTClient
from XRPLib.differential_drive import DifferentialDrive
from XRPLib.defaults import *
import time

drivetrain  = DifferentialDrive.get_default_differential_drive()
reflectance = reflectance.get_default_reflectance()
imu         = IMU.get_default_imu()

class Robot:
    def __init__(self, target_tag_area=2000):
        self.car_id          = 0
        self.target_tag_area = target_tag_area
        self.state           = "IDLE"
        self.corner          = 0
        self.color           = "Pink" #Pink, Green or Black

        print("HuskyLens in tag recognition mode")
        print("HuskyLens ready")

        # init MQTT (no thread)
        print("init mqtt")
        self.mqtt = MQTTClient(
            cmd_topic="topic/xrpinvitational",
        )
        self.mqtt.set_command_callback(self.handle_command)

    def handle_command(self, topic, msg):
        payload = msg.decode("utf-8")
        print(f"Got raw payload: {payload!r}")

        #split if mqtt command is assignments
        parts = payload.replace(":", "").split()
        color_ids = {}
        for i in range(0, len(parts) - 1, 2):
            color = parts[i].lower()
            num   = parts[i+1]
            if num.isdigit():
                color_ids[color] = int(num) - 1

        #set car_id
        my_color = self.color.lower()
        if my_color in color_ids:
            self.car_id = color_ids[my_color] + 1
            print(f"→ Assigned car_id = {self.car_id} for color {self.color!r}")

        #race
        if "go" in parts:
            if self.state == "GET_READY":
                self.state = "RACE"
                print("State set to RACE")

        elif payload.strip() == str(self.car_id):
            # only when the _entire_ payload is exactly your ID
            self.state = "GET_READY"
            print("State set to GET_READY")


    def check_state(self):
        if self.state == "IDLE":
            pass
        elif self.state == "GET_READY":
            self.get_ready()
            pass
        elif self.state == "RACE":
            self.line_follow()
            self.check_april_tag()
            if self.corner:
                self.mqtt.publish(
                    topic=self.mqtt.cmd_topic,
                    msg=str(self.car_id + 1)
                )
                pass
        elif self.state == "END":
            pass

    def check_april_tag(self):

        self.corner = False
        max_dist_area = -1

        data = self.husky.command_request_blocks_learned()
        for block in data:
            x, y, w, h, tag_id = block
            area = w * h
            print(f"Tag {tag_id} has area {area}")

            if tag_id == self.corner_tag_id:
                self.corner = True
                print("Corner tag detected")
                
            elif tag_id == self.distance_tag_id:
                # track the largest area for your distance tag
                if area > max_dist_area:
                    max_dist_area = area

        # once the distance tag is “close enough,” fire your go command
        if max_dist_area >= self.target_tag_area:
            print("→ Distance threshold reached (area="
                f"{max_dist_area}), publishing 'go'")
            # publish on your command topic so everyone hears the start
            self.mqtt.publish(self.mqtt.cmd_topic, "go")

        return max_dist_area


    def line_follow(self, base_effort=0.45):
        right = reflectance.get_left()
        left  = reflectance.get_right()
        error = left - right
        # drivetrain.set_effort(base_effort - error, base_effort + error)
    
    def turn_90_degrees(self,imu, clockwise=True):
        target_angle = 85 #supoposed to be 90 but it was overturning
        direction = -1 if clockwise else 1 

        angle = 0.0
        last_time = time.ticks_ms()

        self.start_turn(clockwise)

        while abs(angle) < target_angle:
            rate_mdps = imu.get_gyro_z_rate() 
            rate_dps = rate_mdps / 1000.0

            current_time = time.ticks_ms()
            dt = time.ticks_diff(current_time, last_time) / 1000.0  
            last_time = current_time

            angle += direction * rate_dps * dt

            time.sleep_ms(5) 

        self.stop_motors()
        print(f"Done turning. Final angle turned: {angle:.2f} degrees")
    
    
    
    def get_ready(self):

        imu = IMU.get_default_imu()

        self.turn_90_degrees(imu, clockwise=True)

        target_heading = imu.get_yaw()
        self.drive_straight_until_line(imu, target_heading)

        drivetrain.set_effort(0.3,0.3)
        time.sleep(0.5)

        self.turn_90_degrees(imu, clockwise=False)
    
    
    
    def drive_straight_until_line(self,imu, target_heading, base_speed=0.4):
        kp = 0.01 

        right = reflectance.get_left()
        left = reflectance.get_right()

        

        while right < 0.9 and left < 0.9:
                
                current_heading = imu.get_yaw() 
                error = current_heading - target_heading

                correction = kp * error

                left_speed = base_speed + correction
                right_speed = base_speed - correction

                drivetrain.set_effort(left_speed,right_speed)

                right = reflectance.get_left()
                left = reflectance.get_right()

                time.sleep(0.1)

        self.stop_motors()
        print("Line detected, stopped.")
        
        

    def run(self, loop_delay=0.01):
        try:
            while True:
                self.mqtt.check_msg()
                self.check_state()

                time.sleep(loop_delay)
                
        except KeyboardInterrupt:
            print("shutting down")


if __name__ == "__main__":
    r = Robot()
    r.run()