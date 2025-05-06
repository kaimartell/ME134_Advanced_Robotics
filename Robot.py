from Husky.huskylensPythonLibrary import HuskyLensLibrary
import time
from PID_controller import PIDController
from MQTT.mqtt import MQTTClient
from XRPLib.differential_drive import DifferentialDrive
drivetrain = DifferentialDrive.get_default_differential_drive()


reflectance = reflectance.get_default_reflectance()


class Robot:
    def __init__(self, husky, car_id, target_tag_area=2000):
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
        
    def handle_command(self, topic, msg):
        cmd = msg.decode

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

        area_list.sort()
        # Return largest area read (-1 if no data)
        return area_list[len(area_list - 1)] if len(area_list) != 0 else -1
    