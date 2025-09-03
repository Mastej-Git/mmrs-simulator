from PyQt5.QtCore import QTimer

import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches



class RobotSimulation(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = figure.add_subplot(111)
        super().__init__(figure)

        self.board_size = 15
        self.position_idxs = [1, 1, 1]
        self.forbidden_positions = [(0, 0), (1, 1), (3, 3)]
        
        self.robot1 = patches.Rectangle(
            (0, 0),
            1, 1,
            facecolor="red",
            edgecolor="black",
            linewidth=0.5
        )

        self.robot2 = patches.Rectangle(
            (1, 1),
            1, 1,
            facecolor="green",
            edgecolor="black",
            linewidth=0.5
        )

        self.robot3 = patches.Rectangle(
            (3, 3),
            1, 1,
            facecolor="#751d16",
            edgecolor="black",
            linewidth=0.5
        )

        self.positions1 = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
            (4, 1), (4, 2), (4, 3), (4, 4),
            (3, 4), (2, 4), (1, 4), (0, 4),
            (0, 3), (0, 2), (0, 1)
        ]

        self.positions2 = [
            (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),
            (11, 1), (12, 1), (13, 1),
            (13, 2), (13, 3), (13, 4), (13, 5), (13, 6),
            (13, 7), (13, 8), (13, 9), (13, 10), (13, 11),
            (13, 12), (13, 13),
            (12, 13), (11, 13), (10, 13), (9, 13), (8, 13),
            (7, 13), (6, 13), (5, 13), (4, 13), (3, 13),
            (2, 13), (1, 13),
            (1, 12), (1, 11), (1, 10), (1, 9), (1, 8),
            (1, 7), (1, 6), (1, 5), (1, 4), (1, 3),
            (1, 2)
        ]

        self.positions3 = [
            (3, 3), (4, 3), (5, 3),
            (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
            (5, 9), (5, 10), (5, 11), (5, 12),
            (4, 12), (3, 12),
            (3, 11), (3, 10), (3, 9), (3, 8), (3, 7),
            (3, 6), (3, 5), (3, 4)
        ]

        for x in range(self.board_size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.add_patch(self.robot1)
        self.ax.add_patch(self.robot2)
        self.ax.add_patch(self.robot3)

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
        if self.position_idxs[0] == len(self.positions1):
            self.position_idxs[0] = 0
        if self.position_idxs[1] == len(self.positions2):
            self.position_idxs[1] = 0
        if self.position_idxs[2] == len(self.positions3):
            self.position_idxs[2] = 0
        if (self.positions1[self.position_idxs[0]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot1.get_xy())
            self.forbidden_positions.append(self.positions1[self.position_idxs[0]])
            self.robot1.set_xy(self.positions1[self.position_idxs[0]])
            self.position_idxs[0] += 1
        if (self.positions2[self.position_idxs[1]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot2.get_xy())
            self.forbidden_positions.append(self.positions2[self.position_idxs[1]])
            self.robot2.set_xy(self.positions2[self.position_idxs[1]])
            self.position_idxs[1] += 1
        if (self.positions3[self.position_idxs[2]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot3.get_xy())
            self.forbidden_positions.append(self.positions3[self.position_idxs[2]])
            self.robot3.set_xy(self.positions3[self.position_idxs[2]])
            self.position_idxs[2] += 1

        # self.robot2.set_xy(self.positions2[self.position_idxs[1]])
        # self.robot3.set_xy(self.positions3[self.position_idxs[2]])
        self.draw()