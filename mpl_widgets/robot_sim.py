from PyQt5.QtCore import QTimer, Qt

import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mpl_widgets.robots import (
    robot0, positions0,
    robot1, positions1,
    robot2, positions2,
    robot3, positions3,
    robot4, positions4,
    robot5, positions5,
    robot6, positions6,
    robot7, positions7,
    robot8, positions8,
    robot9, positions9
)



class RobotSimulation(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = figure.add_subplot(111)
        super().__init__(figure)

        self.simulation_f = False

        self.board_size = 15
        self.position_idxs = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.forbidden_positions = [(0, 0), (1, 1), (3, 3), (12, 12), (14, 14), (0, 14), (14, 0), (14, 5), (9, 0), (2, 6)]

        self.robots = [robot0, robot1, robot2, robot3, robot4, robot5, robot6, robot7, robot8, robot9]
        self.positions = [positions0, positions1, positions2, positions3, positions4, positions5, positions6, positions7, positions8, positions9]

        for x in range(self.board_size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        for robot in self.robots:
            self.ax.add_patch(robot)

        self.ax.set_xlim(0, self.board_size)
        self.ax.set_ylim(0, self.board_size)
        self.ax.set_aspect("equal")
        # self.ax.set_position([0, 0, 1, 1])
        # self.ax.axis("off")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def start_moving(self) -> None:
        self.timer.start(200)

    def reset_pos_idx(self, robot_idx):
        if self.position_idxs[robot_idx] == len(self.positions[robot_idx]):
            self.position_idxs[robot_idx] = 0

    def reset_pos_idx_back(self, robot_idx):
        if self.position_idxs[robot_idx] == -1:
            self.position_idxs[robot_idx] = len(self.positions[robot_idx]) - 1

    def move_robot(self, robot_idx):
        if (self.positions[robot_idx][self.position_idxs[robot_idx]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robots[robot_idx].get_xy())
            self.forbidden_positions.append(self.positions[robot_idx][self.position_idxs[robot_idx]])
            self.robots[robot_idx].set_xy(self.positions[robot_idx][self.position_idxs[robot_idx]])
            self.position_idxs[robot_idx] += 1

    def move_robot_back(self, robot_idx):
        if (self.positions[robot_idx][self.position_idxs[robot_idx]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robots[robot_idx].get_xy())
            self.forbidden_positions.append(self.positions[robot_idx][self.position_idxs[robot_idx]])
            self.robots[robot_idx].set_xy(self.positions[robot_idx][self.position_idxs[robot_idx]])
            self.position_idxs[robot_idx] -= 1

    def update_position(self) -> None:

        for i in range(len(self.robots)):
            self.reset_pos_idx(i)

        for i in range(len(self.robots)):
            self.move_robot(i)

        self.draw()

    def update_position_back(self) -> None:

        for i in range(len(self.robots)):
            self.reset_pos_idx_back(i)

        for i in range(len(self.robots)):
            self.move_robot_back(i)

        self.draw()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.simulation_f is False:
                self.timer.start(200)
                self.simulation_f = True
            else:
                self.timer.stop()
                self.simulation_f = False

        elif event.key() == Qt.Key_Right:
            self.update_position()

        elif event.key() == Qt.Key_Left:
            self.update_position_back()
