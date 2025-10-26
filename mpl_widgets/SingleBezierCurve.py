from PyQt5.QtCore import QTimer, Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np


class Car:

    def __init__(self, path: list[list[tuple[int, int]]], radius: float, car_color: str, path_color: str):
        self.path = path
        self.radius = radius
        self.car_color = car_color
        self.path_color = path_color
        self.t = 0.0

        self.render = patches.Circle(self.path[0][0], self.radius, color=self.car_color)

car1 = Car(
    path=[[(1, 1), (4, 3), (9, 2)]],
    radius=0.3,
    car_color="#12700EFF",
    path_color="#17D220"
)

car2 = Car(
    path=[[(1, 5), (6, 0), (6, 6)]],
    radius=0.3,
    car_color="#0C0FB2",
    path_color="#6494F4"
)

car3 = Car(
    path=[[(1, 3.5), (5, 3), (8, 5)]],
    radius=0.3,
    car_color="#4B0669",
    path_color="#C432AC"
)


class SingleBezierCurve(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)

        self.simulation_f = False

        self.cars = [car1, car2, car3]

        self.draw_square_grid(10)
        self.draw_bezier_curve()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def start_moving(self) -> None:
        self.timer.start(50)

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

        # x, y = zip(*verts)
        # self.ax.plot(x, y, "ro--")


    def draw_bezier_curve(self) -> None:

        for i in range(len(self.cars)):
            self.draw_curve(self.cars[i].path[0], self.cars[i].path_color)
            self.ax.add_patch(self.cars[i].render)

    def update_position(self) -> None:
        for i in range(len(self.cars)):
            if self.cars[i].t > 1.0:
                self.cars[i].t = 0.0

        for i in range(len(self.cars)):
            if not self.check_collision(self.cars[i], i, forward=True):
                self.cars[i].t += 0.01
                self.cars[i].render.center = self.bezier_point(self.cars[i].t, self.cars[i].path[0])

        self.draw()

    def update_position_back(self) -> None:
        for i in range(len(self.cars)):
            if self.cars[i].t < 0.0:
                self.cars[i].t = 1.0

        for i in range(len(self.cars)):
            if not self.check_collision(self.cars[i], i, forward=False):
                self.cars[i].t -= 0.01
                self.cars[i].render.center = self.bezier_point(self.cars[i].t, self.cars[i].path[0])

        self.draw()

    def check_collision(self, car_a, car_idx, forward=True) -> None:
        x1, y1 = self.bezier_point(self.cars[car_idx].t + (0.01 if forward else -0.01), self.cars[car_idx].path[0])
        r_a = self.cars[car_idx].radius
        cars_rest = self.cars.copy()
        cars_rest.remove(car_a)
        for j in range(len(cars_rest)):
            r_b = cars_rest[j].radius
            x2, y2 = cars_rest[j].render.center
            dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            if dist <= (r_a + r_b + 0.1):
                return True
        return False
    
    def keyPressEvent(self, event) -> None:
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
