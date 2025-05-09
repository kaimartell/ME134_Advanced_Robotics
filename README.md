XRP Relay Robot README
Summary
This guide shows you how to set up three XRP robots equipped with a HuskyLens AI camera and line sensors to run a relay‐style lap using MQTT commands. 

Prerequisites
XRP Control Board with MicroPython 2.0.1 firmware

HuskyLens AI Vision Sensor with Qwiic cable 

Reflectance line sensor (e.g. Qwiic Reflectance)

Wi‑Fi network (SSID & password)

MQTT broker on your LAN (TCP on port 1883)


1. Hardware Setup
Mount the HuskyLens on your XRP board via the Qwiic cable, make sure I²C pins match (SCL→pin19, SDA→pin18) 

Attach the line sensor under the front of the robot via Qwiic cable to the line port, centered so that both reflectance cells read the tape line.

Power on the XRP board via USB, verify the HuskyLens displays its menu.


2. MicroPython Libraries
XRPLib (control motors, IMU, reflectance)

HuskyLens MicroPython library (tag recognition, block reads)

Paho MQTT client (MicroPython port)


3. Configure Robot Code
In robot.py, set your robot’s color:
    self.color = "Pink"  # or "Green", "Black"

In mqtt.py, update SSID/wifi_pass if your network differs from tufts_eecs/foundedin1883

Make sure the command topic matches your broker:
    cmd_topic="topic/xrpinvitational"

Adjust target_tag_area in Robot.__init__() for your stop threshold


4. Configure Your MQTT Broker
Confirm your broker (e.g., Mosquitto) is running on port 1883 and accepts connections from your XRP boards 

No TLS/WSS is required for MicroPython clients—raw TCP is fine


5. Upload Code to XRP
In VS Code or the web editor, copy robot.py, main.py, mqtt.py, and all library files into the XRP’s filesystem.

Save and reset each board; you should see:
HuskyLens in tag recognition mode
HuskyLens ready
init mqtt
Config file 'config.txt' not found; using defaults.
Connecting to Wi-Fi SSID='tufts_eecs'...
Wi-Fi connected; IP=10.5.13.129
MQTT: Connected to 10.247.137.92:1883 as XRP-Client_<id>
Subscribed to 'topic/xrpinvitational'


6. Align and Arm
Place all three robots parallel along the tape line at the start

Make sure their front reflectance sensors hover ~1 cm above the line

Verify HuskyLens sees no AprilTags yet (so they stay in IDLE)


7. Run the Relay
Broadcast the assignments from any MQTT client:
    mosquitto_pub -h 10.247.137.92 -t topic/xrpinvitational \
        -m "Pink: 1 Green: 2 Black: 3"

Send the start signal:
    mosquitto_pub -h 10.247.137.92 -t topic/xrpinvitational -m "1"


8. Troubleshooting
No MQTT output:
Check Wi‑Fi status on the robot console.
Confirm broker logs that a new client connected (look for the Client <id> connected line).

Tag detection failures:
Adjust self.husky.tag_recognition_mode() timing or call it once in __init__ 

Line‐following drift:
Tune your PID gains in line_follow() (use XRPLib’s PIDController)



# XRP Relay Robot README

## Summary

This guide shows you how to set up three XRP robots equipped with a HuskyLens AI camera and line sensors to run a relay‐style lap using MQTT commands.

## Prerequisites

- XRP Control Board with MicroPython 2.0.1 firmware  
- HuskyLens AI Vision Sensor with Qwiic cable  
- Reflectance line sensor (e.g. Qwiic Reflectance)  
- Wi‑Fi network (SSID & password)  
- MQTT broker on your LAN (TCP on port 1883)  

## Hardware Setup

1. Mount the HuskyLens on your XRP board via the Qwiic cable, make sure I²C pins match (SCL→pin19, SDA→pin18)  
2. Attach the line sensor under the front of the robot via Qwiic cable to the line port, centered so that both reflectance cells read the tape line.  
3. Power on the XRP board via USB, verify the HuskyLens displays its menu.  

## MicroPython Libraries

- XRPLib (control motors, IMU, reflectance)  
- HuskyLens MicroPython library (tag recognition, block reads)  
- Paho MQTT client (MicroPython port)  

## Configure Robot Code

In `robot.py`, set your robot’s color:

```python
self.color = "Pink"  # or "Green", "Black"

In `mqtt.py`, update SSID/wifi_pass if your network differs from tufts_eecs/foundedin1883

Make sure the command topic matches your broker:
```python    
    cmd_topic="topic/xrpinvitational"

Adjust target_tag_area in Robot.__init__() for your stop threshold
