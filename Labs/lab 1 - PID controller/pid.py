import time
import math

class PID:
    def __init__(self, kp, ki, kd, target_speed=0, feed_forward=0.5, min_effort=0.2, max_effort=1.0):
        """
        Initializes the PID controller with a feed-forward term and minimum effort.
        
        :param kp: Proportional gain.
        :param ki: Integral gain.
        :param kd: Derivative gain.
        :param target_speed: Desired forward speed (always positive).
        :param feed_forward: Baseline effort needed to roughly maintain target speed.
        :param min_effort: Minimum allowed effort (prevents turning completely off).
        :param max_effort: Maximum allowed effort.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target_speed = target_speed
        self.feed_forward = feed_forward
        self.min_effort = min_effort
        self.max_effort = max_effort
        
        self.previous_error = 0
        self.integral = 0
        self.previous_time = None

    def calculate_effort(self, current_speed):
        """
        Calculates the motor effort using PID logic with a feed-forward term.
        Instead of forcing zero output when error < 0, we allow a small correction.
        The final command is clipped between min_effort and max_effort.
        
        :param current_speed: Effective forward speed (always positive when moving forward).
        :return: A duty cycle between min_effort and max_effort.
        """
        current_time = time.time()
        error = self.target_speed - current_speed

        # On first call, initialize time and error.
        if self.previous_time is None:
            self.previous_time = current_time
            self.previous_error = error
            dt = 0.2  # assume sampling interval
        else:
            dt = current_time - self.previous_time
            if dt < 0.01:
                dt = 0.01  # avoid extreme derivative values

        # Accumulate the integral if error is positive, otherwise allow it to decay.
        if error > 0:
            self.integral += error * dt
        else:
            self.integral *= 0.9  # decay integral when error is negative

        derivative = (error - self.previous_error) / dt

        # PID correction
        correction = self.kp * error + self.ki * self.integral + self.kd * derivative

        # Add feed-forward term to get overall command.
        raw_effort = self.feed_forward + correction
        print('error:', error, 'integral:', self.integral, 'derivative:', derivative, 'raw_effort:', raw_effort)

        # Clip the effort between min_effort and max_effort.
        final_effort = max(self.min_effort, min(self.max_effort, raw_effort))

        # Update for next call.
        self.previous_error = error
        self.previous_time = current_time

        return final_effort

    def set_target_speed(self, target_speed):
        self.target_speed = target_speed

    def reset(self):
        self.previous_error = 0
        self.integral = 0
        self.previous_time = None
