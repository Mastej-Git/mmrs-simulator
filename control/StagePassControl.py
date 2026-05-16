import numpy as np

class StagePassControl:
    """
    Translates the discrete-event supervisor state (running/iddling, sector
    boundaries t_query / t_critical) into a continuous-time velocity setpoint
    that is handed to RobotMotionControl.

    Speed profile (per curve):
      - Trapezoidal: accelerate from min_speed at t=0, decelerate to
        end_speed before t=1 (0 on the last curve, min_speed otherwise).
      - Sector-aware: additionally brake to 0 at t_critical of any upcoming
        conflict sector whose resources have not yet been granted (PH).
        If the robot is already past t_critical without the resources, the
        setpoint is forced to 0 (the supervisor must stop it).
    """

    def __init__(self, robot):
        self.robot = robot
        self.target_v = 0.0
        self.min_speed_ratio = 0.3

    def get_setpoint(self):
        status = self.robot.state.status
        max_v = self.robot.state.max_v

        if status in ("iddling", "finished"):
            self.target_v = 0.0
        elif status == "running":
            self.target_v = self._compute_adaptive_speed(max_v)
            # self.target_v = max_v

        return self.target_v

    def _compute_adaptive_speed(self, max_v):
        current_curve_idx = self.robot.state.current_curve_idx
        current_t = self.robot.state.current_t

        if not self.robot.path or current_curve_idx >= len(self.robot.path):
            return max_v

        curve_length = self.robot.get_current_curve_length(current_curve_idx)
        max_a = self.robot.state.max_a
        min_speed = max_v * self.min_speed_ratio
        is_last_curve = (current_curve_idx >= len(self.robot.path) - 1)

        remaining_dist = max(0.0, (1.0 - current_t) * curve_length)
        end_speed = 0.0 if is_last_curve else min_speed

        # Trapezoidal profile: max speed constrained by braking distance to end
        max_speed_to_brake = np.sqrt(max(0.0, end_speed ** 2 + 2 * max_a * remaining_dist))
        target_speed = min(max_speed_to_brake, max_v)

        # Sector-aware braking: slow to 0 at t_critical of unacquired sectors
        current_sectors = self.robot.path_sectors.get(current_curve_idx, [])
        for sector in current_sectors:
            if current_t > sector.t_u[0]:
                continue
            if all(r in self.robot.state.PH for r in sector.resource_ids):
                continue
            if sector.t_critical is None:
                continue
            if current_t < sector.t_critical:
                dist_to_critical = max(0.0, (sector.t_critical - current_t) * curve_length)
                brake_speed = np.sqrt(max(0.0, 2 * max_a * dist_to_critical))
                target_speed = min(target_speed, brake_speed)
            else:
                target_speed = 0.0

        # Keep minimum speed on non-terminal sections unless forced to brake
        near_end = is_last_curve and current_t > 0.9
        if target_speed > 0 and not near_end:
            target_speed = max(target_speed, min_speed)

        return max(0.0, target_speed)

    def reset(self):
        self.target_v = 0.0
