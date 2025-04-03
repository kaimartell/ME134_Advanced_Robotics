import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import matplotlib.dates as mdates

# Read the CSV file
df = pd.read_csv("log.csv")

# Convert the timestamp (in ms) to a datetime object; adjust unit if needed.
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

# Prepare data arrays
time_array = df['datetime'].to_numpy()
right_velocity_array = df['right_velocity'].to_numpy()
left_velocity_array = abs(df['left_velocity'].to_numpy())
right_error_array = df['right_error'].to_numpy()
left_error_array = df['left_error'].to_numpy()
right_effort_array = df['right_effort'].to_numpy()
left_effort_array = df['left_effort'].to_numpy()

# --- Plot 1: Velocities ---
fig1, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(time_array, right_velocity_array, marker='o', linewidth=2, label='Right Velocity')
ax1.plot(time_array, left_velocity_array, marker='o', linewidth=2, label='Left Velocity (Absolute)')
ax1.axhline(30, color='red', linestyle='--', linewidth=2, label='Target Speed (30 cm/s)')
ax1.set_ylabel("Velocity (cm/s)")
ax1.set_title("Velocities with PID Control", fontsize=14, fontweight='bold')
ax1.legend(fontsize=12)
ax1.grid(True)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
fig1.autofmt_xdate()

# Enable hover annotations on the velocity plot
cursor1 = mplcursors.cursor(ax1.lines, hover=True)
def format_annotation1(sel):
    x, y = sel.target
    date_str = mdates.num2date(x).strftime('%H:%M:%S')
    sel.annotation.set_text(f"Time: {date_str}\nValue: {y:.2f}")
cursor1.connect("add", format_annotation1)

# --- Plot 2: Velocity Errors ---
fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.plot(time_array, right_error_array, marker='o', linewidth=2, label='Right Velocity Error')
ax2.plot(time_array, left_error_array, marker='o', linewidth=2, label='Left Velocity Error')
ax2.set_ylabel("Velocity Error (cm/s)")
ax2.set_title("Velocity Errors", fontsize=14, fontweight='bold')
ax2.legend(fontsize=12)
ax2.grid(True)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
fig2.autofmt_xdate()

# --- Plot 3: Motor Efforts ---
fig3, ax3 = plt.subplots(figsize=(12, 6))
ax3.plot(time_array, right_effort_array, marker='o', linewidth=2, label='Right Motor Effort')
ax3.plot(time_array, left_effort_array, marker='o', linewidth=2, label='Left Motor Effort')
ax3.set_ylabel("Motor Effort")
ax3.set_title("Motor Efforts", fontsize=14, fontweight='bold')
ax3.legend(fontsize=12)
ax3.grid(True)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
fig3.autofmt_xdate()

plt.show()
