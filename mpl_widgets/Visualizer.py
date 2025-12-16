from PyQt5.QtCore import QTimer, Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
from control.StageTransitionControl import StageTransitionControl



class Sector:
    def __init__(self, limit_inferior: tuple[int, int], limit_superior: tuple[int, int]):
        self.limit_inferior = limit_inferior
        self.limit_superior = limit_superior
        self.adresses_list = []


class Visualizer(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)

        self.simulation_f = False

        self.supervisor = StageTransitionControl(None)
        self.visual_agvs = []

        self.t = [0.0, 0.0]
        self.path_idx = [0, 0]

        self.draw_square_grid(15)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position_forward)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def start_moving(self) -> None:
        self.timer.start(50)

    def bezier_point(self, t: float, verts: list[tuple[int, int]]) -> tuple[float, float]:
        return (
            (1 - t) ** 2 * np.array(verts[0])
            + 2 * (1 - t) * t * np.array(verts[1])
            + t ** 2 * np.array(verts[2])
        )

    def draw_square_grid(self, size=10) -> None:
        for x in range(size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.set_xlim(0, size)
        self.ax.set_ylim(0, size)
        self.ax.set_aspect("equal")

    def draw_curve(self, i: int) -> None:
        for path in self.supervisor.agvs[i].path:
            codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
            path_draw = Path(path, codes)

            patch = patches.PathPatch(path_draw, facecolor="none", lw=2, edgecolor=self.supervisor.agvs[i].path_color)
            self.ax.add_patch(patch)

        # self.draw()

    def draw_add_lines(self, i: int) -> None:
        for positions in self.supervisor.agvs[i].path:
            x, y = zip(*positions)
            self.ax.plot(x, y, "ro--")
        # self.draw()

    def draw_marked_states(self) -> None:
        for agv in self.supervisor.agvs:
            for marked_state in agv.marked_states:
                point = patches.Circle(marked_state, 0.1, color=agv.path_color, zorder=4)
                self.ax.add_patch(point)

    def draw_middle_points(self, i: int) -> None:
        for p in self.supervisor.agvs[i].path:
            point = patches.Circle(p[1], 0.1, color="#EADA62", zorder=4)
            self.ax.add_patch(point)
        # self.draw()

    def draw_bezier_curve(self, i: int) -> None:

        self.draw_marked_states()
        agv = patches.Circle(
            self.supervisor.agvs[i].marked_states[0],
            self.supervisor.agvs[i].radius,
            color=self.supervisor.agvs[i].color,
            zorder=3
        )
        self.visual_agvs.append(agv)
        self.ax.add_patch(self.visual_agvs[i])

        # self.draw()

    def update_position_forward(self) -> None:
        for i in range(len(self.supervisor.agvs)):
            self.t[i] += 0.01
            if self.t[i] > 1.0:
                self.t[i] = 0.0
                self.path_idx[i] += 1
                if self.path_idx[i] == len(self.supervisor.agvs[i].path):
                    self.path_idx[i] = 0

            new_center = self.bezier_point(self.t[i], self.supervisor.agvs[i].path[self.path_idx[i]])
            self.visual_agvs[i].center = new_center

        self.draw()

    def update_position_back(self) -> None:
        for i in range(len(self.supervisor.agvs)):
            self.t[i] -= 0.01
            if self.t[i] < 0.0:
                self.t[i] = 1.0
                self.path_idx[i] -= 1
                if self.path_idx[i] == -1:
                    self.path_idx[i] = len(self.supervisor.agvs[i].path) - 1

            new_center = self.bezier_point(self.t[i], self.supervisor.agvs[i].path[self.path_idx[i]])
            self.visual_agvs[i].center = new_center

        self.draw()

    def reset_simulation(self) -> None:
        for i in range(len(self.supervisor.agvs)):
            self.t[i] = 0
            self.path_idx[i] = 0

            starting_point = self.bezier_point(self.t[i], self.supervisor.agvs[i].path[self.path_idx[i]])
            self.visual_agvs[i].center = starting_point

        self.draw()
            
    
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Space:
            if self.simulation_f is False:
                self.timer.start(50)
                self.simulation_f = True
            else:
                self.timer.stop()
                self.simulation_f = False

        if event.key() == Qt.Key_Q:
            exit(0)

        elif event.key() == Qt.Key_Right:
            self.update_position_forward()

        elif event.key() == Qt.Key_Left:
            self.update_position_back()

