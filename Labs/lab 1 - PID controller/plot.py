import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "ME134/Lab1"

# Data storage
MAX_POINTS = 100  # Number of points to display on the live plot
time_data = deque(maxlen=MAX_POINTS)
right_velocity_data = deque(maxlen=MAX_POINTS)
left_velocity_data = deque(maxlen=MAX_POINTS)
right_effort_data = deque(maxlen=MAX_POINTS)
left_effort_data = deque(maxlen=MAX_POINTS)

# Set up live plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

# Velocity plot
ax1.set_title("Motor Velocity (Target vs Actual)")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Velocity (cm/s)")
line_target, = ax1.plot([], [], "k--", label="Target Speed")
line_right_velocity, = ax1.plot([], [], "r-", label="Right Velocity")
line_left_velocity, = ax1.plot([], [], "b-", label="Left Velocity")
ax1.legend()

# Effort plot
ax2.set_title("Motor Effort")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Effort")
line_right_effort, = ax2.plot([], [], "r-", label="Right Effort")
line_left_effort, = ax2.plot([], [], "b-", label="Left Effort")
ax2.legend()

def on_message(client, userdata, message):
    """ Callback function for when a new MQTT message is received """
    try:
        msg = message.payload.decode("utf-8").strip()
        print(f"Received message: {msg}")   
        data = msg.split(",")
        
        if len(data) == 5:  # Ensure valid data format
            timestamp = float(data[0])
            right_velocity = float(data[1])
            left_velocity = float(data[2])
            right_effort = float(data[3])
            left_effort = float(data[4])

            # Append new data
            time_data.append(timestamp)
            right_velocity_data.append(right_velocity)
            left_velocity_data.append(left_velocity)
            right_effort_data.append(right_effort)
            left_effort_data.append(left_effort)

    except Exception as e:
        print(f"Error processing message: {e}")

def update_plot(frame):
    """ Updates the plot with the latest data (runs on main thread) """
    line_target.set_data(time_data, [20] * len(time_data))  # Target speed is constant
    line_right_velocity.set_data(time_data, right_velocity_data)
    line_left_velocity.set_data(time_data, left_velocity_data)
    line_right_effort.set_data(time_data, right_effort_data)
    line_left_effort.set_data(time_data, left_effort_data)

    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()

def main():
    """ Set up the MQTT client and start listening for messages """
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)

    print(f"Connected to MQTT broker {MQTT_BROKER}, listening for messages on {MQTT_TOPIC}...")

    client.loop_start()  # Start MQTT listener in background

    # Use Matplotlib's animation function to update the plot
    ani = animation.FuncAnimation(fig, update_plot, interval=100)

    plt.show()  # Keep the plot open (this runs on the main thread)

    client.loop_stop()  # Stop MQTT loop when plot is closed

if __name__ == "__main__":
    main()
