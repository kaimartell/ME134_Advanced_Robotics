import time

class PID:
    def __init__(self, kp, ki, kd, target_speed=0, min_effort=0, max_effort=1):
        """
        Init PID Controller
        kp = proportional gain
        ki = integral gain
        kd = derivative gain
        clamp with min and max effort
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target_speed = target_speed
        self.min_effort = min_effort
        self.max_effort = max_effort
        
        self.previous_error = 0.0
        self.integral = 0.0
        self.previous_time = None

    def calculate_effort(self, current_speed):
        """
        Calculate the control effort based on current speed
        use equation effort = kp * error + ki * integral + kd * derivative
        
        """
        current_time = time.time()
        
        # Determine the time difference dt
        if self.previous_time is None:
            dt = 0.05  # Assume a default sample interval for the first call
        else:
            dt = current_time - self.previous_time
            dt = max(dt, 0.01)  

        error = self.target_speed - current_speed

        # Update the integral term
        self.integral += error * dt
        
        # Calculate the derivative term
        derivative = (error - self.previous_error) / dt if self.previous_time is not None else 0.0

        # Calculate the PID correction
        correction = self.kp * error + self.ki * self.integral + self.kd * derivative

        effort = max(self.min_effort, min(self.max_effort, correction))

        # Print for debugging
        print(f"time: {current_time:.5f}, dt: {dt:.3f}, error: {error:.3f}, integral: {self.integral:.3f}, derivative: {derivative:.3f}, raw: {correction:.3f}, effort: {effort:.3f}")

        # Update state for next iteration
        self.previous_error = error
        self.previous_time = current_time

        return effort, error

    def set_target_speed(self, target_speed):
        self.target_speed = target_speed

    def reset(self):
        self.previous_error = 0.0
        self.integral = 0.0
        self.previous_time = None
