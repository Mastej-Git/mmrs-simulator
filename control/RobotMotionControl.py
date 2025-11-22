class RobotMotionControl:

    def __init__(self, robot):
        self.robot = robot
        self.current_speed = 0
        self.current_direction = 0

    def set_speed(self, speed):
        self.current_speed = speed
        self.robot.set_speed(speed)

    def set_direction(self, direction):
        self.current_direction = direction
        self.robot.set_direction(direction)

    def stop(self):
        self.current_speed = 0
        self.robot.stop()