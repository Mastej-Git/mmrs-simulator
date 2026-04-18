import numpy as np

class RobotMotionControl:
    """
    First-order velocity controller with symmetric acceleration and asymmetric
    deceleration (braking is 1.5× faster than acceleration, matching the
    braking-distance model used in StagePassControl).

    When the supervisor sets status to "iddling" or "finished" the controller
    ramps velocity down to zero; it does NOT jump to zero so that the
    continuous-time position remains smooth.
    """

    def __init__(self, robot):
        self.robot = robot
        self.current_velocity = 0.0

    def compute_velocity(self, target_speed, dt):
        curr_status = self.robot.state.status
        max_a = self.robot.state.max_a
        max_v = self.robot.state.max_v

        # Supervisor requested stop — ramp down regardless of target_speed
        if curr_status in ("iddling", "finished"):
            decel = max_a * dt * 1.5
            self.current_velocity = max(0.0, self.current_velocity - decel)
            return self.current_velocity

        velocity_diff = target_speed - self.current_velocity
        delta_accel = max_a * dt
        delta_decel = max_a * dt * 1.5

        if abs(velocity_diff) <= delta_accel:
            self.current_velocity = target_speed
        elif velocity_diff > 0:
            self.current_velocity += delta_accel
        else:
            self.current_velocity -= delta_decel

        self.current_velocity = np.clip(self.current_velocity, 0.0, max_v)
        return self.current_velocity

    def reset(self):
        self.current_velocity = 0.0
