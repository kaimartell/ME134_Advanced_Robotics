## Summary
This project builds a three‑robot relay system (“XRP Invitational”) using MQTT
messaging and AprilTag‐guided robotics. Each robot listens for its turn 
assignment, races its segment by following a line using a line sensor and 
detecting AprilTags to know when to hand off, and then publishes the go‑signal 
to the next robot. Each XRP takes around __ min to complete a lap around the 
track, meaning the entire relay takes around ___ min. 

## Problem
- **Coordinating multiple autonomous robots** in sequence is challenging, 
    especially without a central controller  
- **Reliable inter‑robot communication** is needed to trigger each segment 
    start/stop  
- **Low‑cost hardware** (motors, microcontroller, wheels) means loss of 
    efficiency during drive 

## Approach
1. **Distributed MQTT messaging**  
   - Each robot runs a lightweight MQTT client, subscribing to a 
   "topic/xrpinvitational" topic and publishing its own “go” message when it 
   finishes  
   - Robots can receive their start order with an MQTT command, giving some user
   interface and input

2. **AprilTag detection with HuskyLens**  
   - Robots follow a black tape line using reflectance sensors and a bang-bang 
   controller 
   - When they spot a “corner” AprilTag (ID 1), they set an internal flag  
   - When they detect the next XRP's tag (ID 2) and its area exceeds a threshold
    (indicating close proximity), they publish the next “go” command

3. **Single‐loop architecture**  
   - No threads: all MQTT `check_msg()` and state‐machine logic runs in one main
    loop
   - MicroPython on the microcontroller keeps the footprint small 
    (< 100 kB Flash)


## Results
- **Reliable handoffs** on 10 consecutive runs, 0 failures.  
- **Vision robustness**: AprilTag detection worked under variable lighting and 
    speeds up to 0.5 m/s.  
- **Compact code**: Excluding libraries, python scripts total ~600 lines 

## Impact
- **Scalability**: Adding more robots or segments only requires 
    subscribing/publishing on the same topics—no central server changes  
- **Accessibility**: All code runs on open‑source MicroPython and pure HTML/JS; 
    no middleware
- **Educational value**: Demonstrates distributed control and computer vision

