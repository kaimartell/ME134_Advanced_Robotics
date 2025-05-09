#from XRPLib.differential_drive import DifferentialDrive
from mqtt import *

#drivetrain = DifferentialDrive.get_default_differential_drive()
c = connect_mqtt()
c.ping()

if False: #publishing
    c.publish("topic/message", "Start driving", retain=True)
    drivetrain.set_speed(10,10)
    time.sleep(2)
    c.publish("topic/message", "Stop motors", retain=True)
    drivetrain.set_speed(0,0)
    c.publish("topic/data", str(20), retain=True)
    
    
else: #subscribing
    def handle_message(topic, msg):
        try:
            print(topic)
            print(msg)
            if msg == b'0':
                print("here 1")
                #drivetrain.set_speed(0,0)
            if msg == b'10':
                print("here 2")
                #drivetrain.set_speed(10,10)
                time.sleep(2)
            if msg == b'20':
                print("here 3")
                #drivetrain.set_speed(-10,-10)
                time.sleep(2)
            #drivetrain.set_speed(0,0)
        except:
            print("Exception parsing")
    
    c.set_callback(handle_message)
    c.subscribe("topic/xrpinvitational") 
    while True:
        try:
            c.wait_msg()
        except:
            print("exception")