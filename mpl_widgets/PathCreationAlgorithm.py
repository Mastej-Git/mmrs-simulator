from PyQt5.QtCore import QTimer, Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
from mpl_widgets.AGV import AGV



class Sector:
    def __init__(self, limit_inferior: tuple[int, int], limit_superior: tuple[int, int]):
        self.limit_inferior = limit_inferior
        self.limit_superior = limit_superior
        self.adresses_list = []

agv1 = AGV(
    marked_states=[(1, 1), (3, 6), (5, 2), (8, 7), (4, 7), (9, 12), (2, 13)],
    radius=0.5,
    color="#12700EFF",
    path_color="#17D220",
)

agv2 = AGV(
    marked_states=[(1, 7), (4, 10), (7, 7), (10, 4),  (13, 7)],
    radius=0.5,
    color="#12700EFF",
    path_color="#17D220",
)

agv3 = AGV(
    marked_states=[(13, 7), (10, 10), (7, 7), (4, 4), (1, 7)],
    radius=0.5,
    color="#330DCEFF",
    path_color="#2F75CB",
)

class PathCreationAlgorithm(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)

        self.simulation_f = False

        # self.agvs = [agv1]
        self.agvs = [agv2, agv3]
        self.visual_agvs = []

        self.t = [0.0, 0.0]
        self.path_idx = [0, 0]

        self.draw_square_grid(15)
        for i in range(len(self.agvs)):
            self.draw_bezier_curve(i)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position_forward)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def start_moving(self) -> None:
        self.timer.start(50)

    def bezier_point(self, t: float, verts: list[tuple[int, int]]):
        return (
            (1 - t) ** 2 * np.array(verts[0])
            + 2 * (1 - t) * t * np.array(verts[1])
            + t ** 2 * np.array(verts[2])
        )

    def draw_square_grid(self, size=10):
        for x in range(size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.set_xlim(0, size)
        self.ax.set_ylim(0, size)
        self.ax.set_aspect("equal")

    def bezier_tangent(self, t: float, verts: list[tuple[int, int]]):
        p0, p1, p2 = map(np.array, verts)
        d = 2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1)
        return float(d[0]), float(d[1])

    def _normalize_vec(self, vx: float, vy: float, length: float):
        norm = np.hypot(vx, vy)
        if norm == 0:
            return 0.0, length
        s = length / norm
        return vx * s, vy * s

    def create_path(self, marked_states: list[tuple[int, int]]) -> None:
        bezier_points = []

        start = 0
        end = np.array(marked_states[0])
        
        i = 0
        lap_ms_len = len(marked_states)
        
        while True:

            if i == len(marked_states) - 1:
                break

            if lap_ms_len == len(marked_states):
                start = end
                end = np.array(marked_states[i + 1])
            else:
                start = np.array(marked_states[i])
                end = np.array(marked_states[i + 1])
                lap_ms_len = len(marked_states)
                
            if i == 0:
                orientation = np.array([0, 1])
            else:
                orientation = np.array(self.bezier_tangent(1, bezier_points[i - 1]))

            ti_vec = orientation
            pi_vec = end - start

            middle_point = start + self.agvs[0].radius * (ti_vec / np.linalg.norm(ti_vec))

            self.point = patches.Circle(middle_point, 0.1, color="#FF33BE", zorder=4)
            self.ax.add_patch(self.point)

            angle = np.arccos(np.dot(ti_vec, pi_vec)/(np.linalg.norm(ti_vec)*np.linalg.norm(pi_vec)))
            
            if angle < np.pi/2 and angle > -np.pi/2:
                tmp_list = [tuple(start.tolist()), tuple(middle_point.tolist()), tuple(end.tolist())]
                bezier_points.append(tmp_list)
            else:
                cross = ti_vec[0]*pi_vec[1] - ti_vec[1]*pi_vec[0]
                if cross > 0:
                    ti_vec = np.array([-ti_vec[1], ti_vec[0]])
                else:
                    ti_vec = np.array([ti_vec[1], -ti_vec[0]])
                additional_point = start + self.agvs[0].radius * 2 * (ti_vec / np.linalg.norm(ti_vec))
                tmp_list = [tuple(start.tolist()), tuple(middle_point.tolist()), tuple(additional_point.tolist())]
                marked_states.insert(i + 1, tuple(additional_point.tolist()))
                bezier_points.append(tmp_list)
            i += 1

        return bezier_points

    def draw_curve(self, positions: list[tuple[int, int]], color: str) -> None:
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(positions, codes)

        patch = patches.PathPatch(path, facecolor="none", lw=2, edgecolor=color)
        self.ax.add_patch(patch)

        x, y = zip(*positions)
        self.ax.plot(x, y, "ro--")

    def draw_bezier_curve(self, i) -> None:

        path = self.create_path(self.agvs[i].marked_states.copy())
        print(path)
        self.agvs[i].created_path = path

        for p in path:
            self.draw_curve(p, self.agvs[i].path_color)

        agv = patches.Circle(self.agvs[i].marked_states[0], self.agvs[i].radius, color="#12700EFF", zorder=3)
        self.visual_agvs.append(agv)
        self.ax.add_patch(self.visual_agvs[i])

    def update_position_forward(self):
        for i in range(len(self.agvs)):
            self.t[i] += 0.01
            if self.t[i] > 1.0:
                self.t[i] = 0.0
                self.path_idx[i] += 1
                if self.path_idx[i] == len(self.agvs[i].created_path):
                    self.path_idx[i] = 0

            new_center = self.bezier_point(self.t[i], self.agvs[i].created_path[self.path_idx[i]])
            self.visual_agvs[i].center = new_center

        self.draw()

    def update_position_back(self):
        for i in range(len(self.agvs)):
            self.t[i] -= 0.01
            if self.t[i] < 0.0:
                self.t[i] = 1.0
                self.path_idx[i] -= 1
                if self.path_idx[i] == -1:
                    self.path_idx[i] = len(self.agvs[i].created_path) - 1

            new_center = self.bezier_point(self.t[i], self.agvs[i].created_path[self.path_idx[i]])
            self.visual_agvs[i].center = new_center

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
            self.update_position_forward()

        elif event.key() == Qt.Key_Left:
            self.update_position_back()

