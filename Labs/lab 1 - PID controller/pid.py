import time


class PID:
    def __init__(self, kp, ki, kd, target_speed=0, effort_limit=(-1.0, 1.0)):
        """
        Initializes the PID controller.

        :param kp: Proportional gain
        :param ki: Integral gain
        :param kd: Derivative gain
        :param target_speed: Desired target speed
        :param effort_limit: Tuple (min_effort, max_effort) to constrain motor effort
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target_speed = target_speed
        self.effort_limit = effort_limit

        self.previous_error = 0
        self.integral = 0
        self.previous_time = None

    def calculate_effort(self, current_speed):
        """
        Calculates the motor effort using PID logic to reach the target speed.

        :param current_speed: Current speed of the motor
        :return: Effort value to set to the motor
        """ 
        current_time = time.time()
        if self.previous_time is None:
            self.previous_time = current_time


        error = self.target_speed - current_speed

        delta_time = current_time - self.previous_time
        if delta_time <= 0:
            delta_time = 1e-6 

        # Proportional term
        proportional = self.kp * error
        print("Proportional: ", proportional)

        # Integral term
        self.integral += error * delta_time
        integral = self.ki * self.integral
        print("Integral: ", integral)   

        # Derivative term
        derivative = self.kd * (error - self.previous_error) / delta_time
        print("Derivative: ", derivative)

        # PID output
        effort = proportional + integral + derivative

        # constrain effort
        #effort = max(self.effort_limit[0], min(self.effort_limit[1], effort))
        #print("Effort: ", effort)

        max_effort_unscaled = max(abs(effort), 1e-6)  # Prevent divide-by-zero
        effort_scaled = effort / max_effort_unscaled  # Scale between -1 and 1

        # Prevent sudden reversals
        if (current_speed > 0 and effort_scaled < 0) or (current_speed < 0 and effort_scaled > 0):
            effort_scaled = 0

        self.previous_error = error
        self.previous_time = current_time

        return effort_scaled

    def set_target_speed(self, target_speed):
        self.target_speed = target_speed

    def reset(self):
        self.previous_error = 0
        self.integral = 0
        self.previous_time = None
