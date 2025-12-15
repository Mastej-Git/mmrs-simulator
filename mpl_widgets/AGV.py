import matplotlib.patches as patches


class AGV:

    def __init__(self, marked_states: list[tuple[int, int]], radius: float, color: str, path_color: str):
        self.marked_states = marked_states
        self.orientation = 0.0
        self.radius = radius
        self.color = color
        self.path_color = path_color
        self.t = 0.0
        self.path = []

        self.render = patches.Circle(self.marked_states[0], self.radius, color=self.color)
        self.created_path = []
