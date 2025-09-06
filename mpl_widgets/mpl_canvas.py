from PyQt5.QtCore import QTimer
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches
# import matplotlib.pyplot as plt
import numpy as np


# class MplCanvas(FigureCanvas):
    
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.ax = fig.add_subplot(111)
#         super().__init__(fig)

#         self.draw_square_grid(10)
#         self.draw_bezier_curve()

#         self.t = 0.0
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_position)

#     def start_moving(self) -> None:
#         self.timer.start(200)

#     def bezier_point(self, t, verts):
#         p0, p1, p2, p3 = verts
#         return (
#             (1 - t) ** 3 * np.array(p0)
#             + 3 * (1 - t) ** 2 * t * np.array(p1)
#             + 3 * (1 - t) * t ** 2 * np.array(p2)
#             + t ** 3 * np.array(p3)
#         )

#     def draw_square_grid(self, size=10):
#         for x in range(size + 1):
#             self.ax.axhline(x, color="gray", linewidth=0.5)
#             self.ax.axvline(x, color="gray", linewidth=0.5)

#         self.ax.set_xlim(0, size)
#         self.ax.set_ylim(0, size)
#         self.ax.set_aspect("equal")

#     def draw_curve(self, positions: list[tuple[int]], color: str) -> None:
#         verts = positions
#         codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
#         path = Path(verts, codes)

#         patch = patches.PathPatch(path, facecolor="none", lw=2, edgecolor=color)
#         self.ax.add_patch(patch)

#         # x, y = zip(*verts)
#         # self.ax.plot(x, y, "ro--")


#     def draw_bezier_curve(self):
#         verts = [
#             (1, 1),
#             (3, 3),
#             (7, 3),
#             (9, 2)
#         ]
#         self.draw_curve(verts, "green")

#         self.car = patches.Circle(verts[0], 0.15, color="red")
#         self.ax.add_patch(self.car)

#         # verts = [
#         #     (1, 6.5),
#         #     (4, 2),
#         #     (7, 2),
#         #     (6, 7)
#         # ]
#         # self.draw_curve(verts, "blue")

#         # verts = [
#         #     (1, 3.5),
#         #     (4, 3),
#         #     (7, 4),
#         #     (8, 6.5)
#         # ]
#         # self.draw_curve(verts, "#9F1989")

#     def update_position(self):
#         verts = [
#             (1, 1),
#             (3, 3),
#             (7, 3),
#             (9, 2)
#         ]
#         if self.t > 1.0:
#             self.t = 0.0
#         x, y = self.bezier_point(self.t, verts)
#         self.car.center = (x, y)
#         self.draw()
#         self.t += 0.01

class MplCanvas(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)

        self.verts = [
            [(1, 1), (4, 3), (9, 2)],
            [(1, 5), (6, 0), (6, 6)],
            [(1, 3.5), (5, 3), (8, 5)]
        ]   

        self.draw_square_grid(10)
        self.draw_bezier_curve()

        self.t = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

    def start_moving(self) -> None:
        self.timer.start(50)

    def bezier_point(self, t, verts):
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

    def draw_curve(self, positions: list[tuple[int]], color: str) -> None:
        verts = positions
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(verts, codes)

        patch = patches.PathPatch(path, facecolor="none", lw=2, edgecolor=color)
        self.ax.add_patch(patch)

        # x, y = zip(*verts)
        # self.ax.plot(x, y, "ro--")


    def draw_bezier_curve(self):

        self.draw_curve(self.verts[0], "#17D220")

        self.car1 = patches.Circle(self.verts[0][0], 0.3, color="#12700EFF")
        self.ax.add_patch(self.car1)

        self.draw_curve(self.verts[1], "#6494F4")

        self.car2 = patches.Circle(self.verts[1][0], 0.3, color="#0C0FB2")
        self.ax.add_patch(self.car2)

        self.draw_curve(self.verts[2], "#C432AC")

        self.car3 = patches.Circle(self.verts[2][0], 0.3, color="#4B0669")
        self.ax.add_patch(self.car3)

    def update_position(self):
        if self.t > 1.0:
            self.t = 0.0
        x, y = self.bezier_point(self.t, self.verts[0])
        self.car1.center = (x, y)
        x, y = self.bezier_point(self.t, self.verts[1])
        self.car2.center = (x, y)
        x, y = self.bezier_point(self.t, self.verts[2])
        self.car3.center = (x, y)
        self.draw()
        self.t += 0.01

