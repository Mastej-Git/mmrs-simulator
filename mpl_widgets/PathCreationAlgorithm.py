from PyQt5.QtCore import QTimer, Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np


class Car:

    def __init__(self, path: list[list[tuple[int, int]]], marked_states: list[tuple[int, int]], radius: float, car_color: str, path_color: str):
        self.path = path
        self.marked_states = marked_states
        self.orientation = 0.0
        self.radius = radius
        self.car_color = car_color
        self.path_color = path_color
        self.t = 0.0

        self.render = patches.Circle(self.path[0][0], self.radius, color=self.car_color)

car1 = Car(
    path=[
        [(1, 1), (4, 3), (6, 2)],
        [(6, 2), (8, 1), (8, 7)],
        [(8, 7), (7, 10), (2, 9)]
    ],
    marked_states=[(1, 1), (6, 2), (8, 7), (2, 9)],
    radius=0.3,
    car_color="#12700EFF",
    path_color="#17D220"
)

class PathCreationAlgorithm(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)

        self.simulation_f = False

        self.cars = [car1]

        self.t = [0.0]
        self.path_idx = 0

        self.draw_square_grid(10)
        self.draw_bezier_curve()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def start_moving(self) -> None:
        self.timer.start(50)

    def create_path(self, points: list[tuple[int, int]]) -> None:
        pass

    def bezier_point(self, t: float, verts: list[tuple[int, int]]):
        p0, p1, p2 = verts
        return (
            (1 - t) ** 2 * np.array(p0)
            + 2 * (1 - t) * t * np.array(p1)
            + t ** 2 * np.array(p2)
        )

    def draw_square_grid(self, size=10):
        for x in range(size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.set_xlim(0, size)
        self.ax.set_ylim(0, size)
        self.ax.set_aspect("equal")

    def draw_curve(self, positions: list[tuple[int, int]], color: str) -> None:
        verts = positions
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(verts, codes)

        patch = patches.PathPatch(path, facecolor="none", lw=2, edgecolor=color)
        self.ax.add_patch(patch)

        x, y = zip(*verts)
        self.ax.plot(x, y, "ro--")


    def draw_bezier_curve(self) -> None:

        self.draw_curve(self.cars[0].path[0], "#17D220")
        self.draw_curve(self.cars[0].path[1], "#6494F4")
        self.draw_curve(self.cars[0].path[2], "#593997")

        self.car1 = patches.Circle(self.cars[0].path[0][0], 0.3, color="#12700EFF", zorder=3)
        self.ax.add_patch(self.car1)

        # Heading (orientation) arrow
        self._heading_len = 0.6  # visual arrow length in grid units

        vx, vy = self.bezier_tangent(self.t[0], self.cars[0].path[self.path_idx])
        vx, vy = self._normalize_vec(vx, vy, self._heading_len)
        cx, cy = self.car1.center
        self.heading_arrow = patches.FancyArrowPatch(
            (cx, cy), (cx + vx, cy + vy),
            arrowstyle='-|>',
            color='#1f1f1f',
            mutation_scale=12,
            lw=1.2,
            zorder=4
        )
        self.ax.add_patch(self.heading_arrow)

    def bezier_tangent(self, t: float, verts: list[tuple[int, int]]):
        """Return the derivative (tangent vector) of a quadratic Bezier at t.
        verts: [p0, p1, p2]
        """
        p0, p1, p2 = map(np.array, verts)
        d = 2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1)
        return float(d[0]), float(d[1])

    def _normalize_vec(self, vx: float, vy: float, length: float):
        norm = np.hypot(vx, vy)
        if norm == 0:
            return 0.0, length  # default up arrow if degenerate
        s = length / norm
        return vx * s, vy * s

    def update_position(self):
        for i in range(len(self.cars)):
            if self.t[i] > 1.0:
                self.t[i] = 0.0
                self.path_idx += 1
                if self.path_idx == len(self.cars[0].path):
                    self.path_idx = 0

            new_center = self.bezier_point(self.t[0], self.cars[0].path[self.path_idx])
            self.car1.center = new_center

            vx, vy = self.bezier_tangent(self.t[0], self.cars[0].path[self.path_idx])
            vx, vy = self._normalize_vec(vx, vy, self._heading_len)
            cx, cy = new_center
            self.heading_arrow.set_positions((cx, cy), (cx + vx, cy + vy))

        self.t[0] += 0.01

        self.draw()

    def update_position_back(self):
        for i in range(len(self.cars)):
            if self.t[i] < 0.0:
                self.t[i] = 1.0
                self.path_idx -= 1
                if self.path_idx == -1:
                    self.path_idx = len(self.cars[0].path) - 1

            new_center = self.bezier_point(self.t[0], self.cars[0].path[self.path_idx])
            self.car1.center = new_center

            vx, vy = self.bezier_tangent(self.t[0], self.cars[0].path[self.path_idx])
            vx, vy = self._normalize_vec(vx, vy, self._heading_len)
            cx, cy = new_center
            self.heading_arrow.set_positions((cx, cy), (cx + vx, cy + vy))

        self.t[0] -= 0.01

        self.draw()
    
    def keyPressEvent(self, event):
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
            self.update_position()

        elif event.key() == Qt.Key_Left:
            self.update_position_back()

