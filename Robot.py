from Husky.huskylensPythonLibrary import HuskyLensLibrary
import time
from PID_controller import PIDController
from MQTT.mqtt import MQTTClient
from XRPLib.differential_drive import DifferentialDrive
from XRPLib.defaults import *


drivetrain = DifferentialDrive.get_default_differential_drive()
reflectance = reflectance.get_default_reflectance()
imu = IMU.get_default_imu()


class Robot:
    def __init__(self, husky, target_tag_area=2000):
        self.husky = husky
        self.car_id
        self.target_tag_area = target_tag_area

        self.state = 'IDLE'
        self.husky.tag_recognition_mode() # Switch to tag recon mode
        self.line_PID = PIDController(0, 0, 0)
        self.corner = 0
        
        self.mqtt = MQTTClient()
        self.mqtt.set_command_callback(self.handle_command)
        self.mqtt.subscribe_commands()
        self.mqtt.start(on_thread=True)
        
    def set_car_id(self, id):
        self.car_id = id
        
    def handle_command(self, msg):
        cmd = msg.decode
        print(cmd)
        if cmd.startswith("Assignment:"):
            self.car_id = int(cmd.split(":")[1])
        if cmd == "go":
            self.state = "RACE"        
        elif cmd == self.car_id:
            self.state = "GET_READY"
        
        
    def tell_next(self, cmd):
        if cmd == "Rounding corner":
            self.mqtt.publish(self.car_id + 1)
        elif cmd == "Pass Baton":
            self.mqtt.publish("go")

    def check_state(self):
        if self.state == 'IDLE':
            # Wait for commands from MQTT
            pass
        elif self.state == 'GET_READY':
            # Drive up to the line and wait to start
            pass
        elif self.state == 'RACE':
            # Drive around the track using line following
            self.line_follow()

            # Search for april tags
            #       if corner found (id=1), do something
            #       if close to next tag, stop, drop, and roll
            area = self.check_april_tag()
            if self.corner:
                # SEND MQTT 
                pass
            if area > self.target_tag_area:
                self.state == 'END'
            
        elif self.state == 'END':
            # Drive back to start area
            pass

    def line_follow(self, base_effort = 0.45):
 
        right = reflectance.get_left()
        left = reflectance.get_right()
        
        error = left-right

        controller = PIDController(1,0,0.75)

        effort = controller.update(error)

        drivetrain.set_effort(base_effort - effort, base_effort + effort)

    def check_april_tag(self):
        corner = 0
        area_list = []
        data = self.husky.command_request_blocks_learned()
        # Parse through available tags
        for i in data:

            # data
            tag_x = i[0]
            tag_y = i[1]
            area = i[2]*i[3]
            id = i[4]

            # if the 0th tag is found, corner flag goes high
            if id == 0:
                self.corner = 1
            else:
                area_list.append(area)
            print(f'Tag {id} has an area of {area}')
            
        #if track apriltag found
        #tell_next("Rounding corner")
        
        #if next car found
        #tell_next("Pass Baton")

        area_list.sort()
        # Return largest area read (-1 if no data)
        return area_list[len(area_list - 1)] if len(area_list) != 0 else -1
    

    def start_turn(self,clockwise=True):
        if clockwise:
            print("Turning clockwise...")
            drivetrain.set_effort(0.4,-0.4)
        else:
            print("Turning counter-clockwise...")
            drivetrain.set_effort(-0.4,0.4)

    
    def stop_motors(self):
        print("Motors stopped.")
        drivetrain.set_effort(0,0)

    
    
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

    
    def drive_straight_until_line(self,imu, target_heading, base_speed=0.4):
        kp = 0.01 

        right = reflectance.get_left()
        left = reflectance.get_right()

        

        while right < 0.9 and left < 0.9:
                
                current_heading = imu.get_yaw() 
                error = current_heading - target_heading


                #print(f"Right sensor: {right}, Left sensor: {left}")
                #print(f"Current heading: {current_heading} Target heading {target_heading}")
                #print(error)

                correction = kp * error

                left_speed = base_speed + correction
                right_speed = base_speed - correction

                drivetrain.set_effort(left_speed,right_speed)

                right = reflectance.get_left()
                left = reflectance.get_right()

                time.sleep(0.1)

        self.stop_motors()
        print("Line detected, stopped.")


    
    def get_ready(self):

        imu = IMU.get_default_imu()

        #Turns right CW 90 degees
        self.turn_90_degrees(imu, clockwise=True)

        #Goes straight until it finds the line
        target_heading = imu.get_yaw()
        self.drive_straight_until_line(imu, target_heading)

        #Moves foward just a bit
        drivetrain.set_effort(0.3,0.3)
        time.sleep(0.5)

        #Turns CCW to sit up line
        self.turn_90_degrees(imu, clockwise=False)