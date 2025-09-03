from PyQt5.QtCore import QTimer

import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mpl_widgets.robots import robot0, positions0, robot1, positions1, robot2, positions2



class RobotSimulation(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = figure.add_subplot(111)
        super().__init__(figure)

        self.board_size = 15
        self.position_idxs = [1, 1, 1]
        self.forbidden_positions = [(0, 0), (1, 1), (3, 3)]

        self.robot0 = robot0
        self.robot1 = robot1
        self.robot2 = robot2
        self.positions0 = positions0
        self.positions1 = positions1
        self.positions2 = positions2

        for x in range(self.board_size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.add_patch(self.robot0)
        self.ax.add_patch(self.robot1)
        self.ax.add_patch(self.robot2)

        self.ax.set_xlim(0, self.board_size)
        self.ax.set_ylim(0, self.board_size)
        self.ax.set_aspect("equal")
        # self.ax.set_position([0, 0, 1, 1])
        # self.ax.axis("off")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

    def start_moving(self) -> None:
        self.timer.start(200)

    def update_position(self) -> None:
        # for i in range(len(self.position_idxs)):
        #     self.position_idxs[i] += 1
        if self.position_idxs[0] == len(self.positions0):
            self.position_idxs[0] = 0
        if self.position_idxs[1] == len(self.positions1):
            self.position_idxs[1] = 0
        if self.position_idxs[2] == len(self.positions2):
            self.position_idxs[2] = 0
        if (self.positions0[self.position_idxs[0]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot0.get_xy())
            self.forbidden_positions.append(self.positions0[self.position_idxs[0]])
            self.robot0.set_xy(self.positions0[self.position_idxs[0]])
            self.position_idxs[0] += 1
        if (self.positions1[self.position_idxs[1]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot1.get_xy())
            self.forbidden_positions.append(self.positions1[self.position_idxs[1]])
            self.robot1.set_xy(self.positions1[self.position_idxs[1]])
            self.position_idxs[1] += 1
        if (self.positions2[self.position_idxs[2]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot2.get_xy())
            self.forbidden_positions.append(self.positions2[self.position_idxs[2]])
            self.robot2.set_xy(self.positions2[self.position_idxs[2]])
            self.position_idxs[2] += 1

        # self.robot2.set_xy(self.positions2[self.position_idxs[1]])
        # self.robot3.set_xy(self.positions3[self.position_idxs[2]])
        self.draw()
