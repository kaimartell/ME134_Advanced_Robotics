import matplotlib.pyplot as plt
import numpy as np

# Robot initial pose
x_robot, y_robot = 0, 0
theta_robot = 0  # in radians

# Waypoint coordinates
x_way, y_way = 0.4, 0.5

plt.figure(figsize=(6,6))

# Plot global coordinate axes (dashed)
plt.arrow(-0.5, 0, 1, 0, head_width=0.03, head_length=0.05, fc='k', ec='k', linestyle='--')
plt.arrow(0, -0.5, 0, 1, head_width=0.03, head_length=0.05, fc='k', ec='k', linestyle='--')
plt.text(0.9, -0.05, 'Global X', fontsize=10, color='k')
plt.text(-0.1, 0.9, 'Global Y', fontsize=10, color='k')

# Plot robot's local coordinate frame (since theta=0, it aligns with global)
plt.arrow(x_robot, y_robot, 0.3, 0, head_width=0.03, head_length=0.05, fc='b', ec='b')
plt.text(0.32, 0.02, 'Local X', fontsize=10, color='b')
plt.arrow(x_robot, y_robot, 0, 0.3, head_width=0.03, head_length=0.05, fc='r', ec='r')
plt.text(0.02, 0.32, 'Local Y', fontsize=10, color='r')

# Draw robot as a triangle (pointing to positive x)
robot_length = 0.2  # length of the robot
robot_width = 0.1   # width of the robot
# Define triangle vertices relative to the robot's center
triangle = np.array([[robot_length, 0], [-robot_length/2, robot_width/2], [-robot_length/2, -robot_width/2]])
# Since theta = 0, no rotation needed; just translate to robot position
triangle[:, 0] += x_robot
triangle[:, 1] += y_robot
plt.fill(triangle[:, 0], triangle[:, 1], 'g', alpha=0.5, label='Robot')

# Plot waypoint as a black dot
plt.plot(x_way, y_way, 'ko', markersize=8)
plt.text(x_way + 0.02, y_way + 0.02, 'Waypoint', fontsize=10, color='k')

# Formatting plot
plt.xlim(-0.5, 1)
plt.ylim(-0.5, 1)
plt.xlabel('X (m)')
plt.ylabel('Y (m)')
plt.title('Robot and Waypoint with Global and Local Frames')
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(True)
plt.show()
