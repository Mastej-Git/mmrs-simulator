import numpy as np
from dataclasses import dataclass
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QDoubleSpinBox, QGroupBox, QGridLayout,
    QSplitter, QScrollArea,
)
from PyQt5.QtCore import Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.patches import Circle

from control.PathCreationAlgorithm import PathCreationAlgorithm
from utils.StyleSheetDark import StyleSheetDark
from utils.StyleSheetLight import StyleSheetLight


_DEFAULT_WAYPOINTS: list[tuple[float, float]] = [
    (0.0, 0.0),
    (5.0, 1.0),
    (2.0, 3.0),
    (0.0, 5.0),
    (3.0, 7.0),
]
_DEFAULT_RADIUS = 1.5
_DEFAULT_ORIENT_DEG = 0.0


@dataclass
class _PathStep:
    step_num: int
    start: np.ndarray
    end: np.ndarray
    ti_vec: np.ndarray
    pi_vec: np.ndarray
    middle_point: np.ndarray
    angle_deg: float
    is_uturn: bool
    rotated_ti: Optional[np.ndarray]
    additional_point: Optional[np.ndarray]
    curve: list
    completed_curves: list
    all_waypoints: list
    waypoint_labels: list
    is_final: bool = False


def _midpoint_label(a: str, b: str) -> str:
    """Return the label halfway between two waypoint labels: "W1","W2" → "W1.5"."""
    mid = (float(a[1:]) + float(b[1:])) / 2.0
    return f"W{mid:g}"


class PathStepsTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._algorithm = PathCreationAlgorithm()
        self._steps: list[_PathStep] = []
        self._current_step: int = 0

        self._build_ui()
        self._recompute()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)

        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        self._fig = Figure(figsize=(6, 6), facecolor="#FFFFFF")
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("background: #FFFFFF;")

        toolbar = NavigationToolbar2QT(self._canvas, canvas_widget)
        toolbar.setStyleSheet("background: #2e2e2e; color: #b1b1b1;")

        canvas_layout.addWidget(toolbar)
        canvas_layout.addWidget(self._canvas)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(260)
        scroll.setStyleSheet(
            "QScrollArea { background: #12121E; border: none; }"
            "QScrollBar:vertical { width: 6px; background: #1A1A2E; }"
            "QScrollBar::handle:vertical { background: #444; border-radius: 3px; }"
        )

        ctrl_widget = QWidget()
        ctrl_widget.setStyleSheet("background: #12121E;")
        ctrl_layout = QVBoxLayout(ctrl_widget)
        ctrl_layout.setContentsMargins(10, 10, 10, 10)
        ctrl_layout.setSpacing(10)

        ctrl_layout.addWidget(self._build_params_group())
        ctrl_layout.addWidget(self._build_step_group())
        ctrl_layout.addWidget(self._build_info_group())
        ctrl_layout.addStretch(1)

        scroll.setWidget(ctrl_widget)

        splitter.addWidget(canvas_widget)
        splitter.addWidget(scroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        root.addWidget(splitter)

    def _build_params_group(self) -> QGroupBox:
        box = QGroupBox("Path Parameters")
        box.setStyleSheet(StyleSheetLight.QGroupBoxStatistics.value)
        grid = QGridLayout(box)
        grid.setSpacing(6)

        grid.addWidget(self._lbl("Radius R"), 0, 0)
        self._spin_radius = self._spinbox(0.1, 500.0, _DEFAULT_RADIUS, 0.5)
        self._spin_radius.valueChanged.connect(self._recompute)
        grid.addWidget(self._spin_radius, 0, 1)

        grid.addWidget(self._lbl("Orient. (°)"), 1, 0)
        self._spin_orient = self._spinbox(-180.0, 180.0, _DEFAULT_ORIENT_DEG, 15.0)
        self._spin_orient.valueChanged.connect(self._recompute)
        grid.addWidget(self._spin_orient, 1, 1)

        btn_reset = QPushButton("Reset Parameters")
        btn_reset.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_reset.setFixedHeight(28)
        btn_reset.clicked.connect(self._on_reset_params)
        grid.addWidget(btn_reset, 2, 0, 1, 2)

        return box

    def _build_step_group(self) -> QGroupBox:
        box = QGroupBox("Step Navigation")
        box.setStyleSheet(StyleSheetLight.QGroupBoxStatistics.value)
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        self._step_label = QLabel("Step: — / —")
        self._step_label.setStyleSheet(
            "color: #00ffff; font-size: 13px; font-weight: bold; background: transparent;"
        )
        self._step_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._step_label)

        row_w = QWidget()
        row_w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(row_w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        self._btn_prev = QPushButton("← Prev")
        self._btn_prev.setStyleSheet(StyleSheetLight.QPushButton.value)
        self._btn_prev.setFixedHeight(32)
        self._btn_prev.clicked.connect(self._on_prev_step)
        row.addWidget(self._btn_prev)

        self._btn_next = QPushButton("Next →")
        self._btn_next.setStyleSheet(StyleSheetLight.QPushButton.value)
        self._btn_next.setFixedHeight(32)
        self._btn_next.clicked.connect(self._on_next_step)
        row.addWidget(self._btn_next)

        layout.addWidget(row_w)

        btn_first = QPushButton("First Step")
        btn_first.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_first.setFixedHeight(26)
        btn_first.clicked.connect(self._on_first_step)
        layout.addWidget(btn_first)

        btn_last = QPushButton("Last Step")
        btn_last.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_last.setFixedHeight(26)
        btn_last.clicked.connect(self._on_last_step)
        layout.addWidget(btn_last)

        btn_points = QPushButton("Only Points")
        btn_points.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_points.setFixedHeight(26)
        btn_points.clicked.connect(self._on_only_points)
        layout.addWidget(btn_points)

        btn_path = QPushButton("Full path")
        btn_path.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_path.setFixedHeight(26)
        btn_path.clicked.connect(self._on_full_path)
        layout.addWidget(btn_path)

        return box

    def _build_info_group(self) -> QGroupBox:
        box = QGroupBox("Step Info")
        box.setStyleSheet(StyleSheetLight.QGroupBoxStatistics.value)
        grid = QGridLayout(box)
        grid.setSpacing(4)

        self._info_type = self._info_val_lbl(grid, 0, "Type:")
        self._info_angle = self._info_val_lbl(grid, 1, "Angle(Ti, Pi):")
        self._info_start = self._info_val_lbl(grid, 2, "Start:")
        self._info_end = self._info_val_lbl(grid, 3, "End:")

        sep = QLabel()
        sep.setFixedHeight(6)
        sep.setStyleSheet("background: transparent;")
        grid.addWidget(sep, 4, 0, 1, 2)

        legend = QLabel(
            "Ti — orientation     green arrow\n"
            "Pi — to next wp    red arrow\n"
            "P1 — mid point     orange ×\n"
            "Ti'— rotated Ti     magenta arrow\n"
            "●  — robot circle   blue dashed\n"
            "── completed curves  gray"
        )
        legend.setStyleSheet("color: #666; font-size: 9px; background: transparent;")
        grid.addWidget(legend, 5, 0, 1, 2)

        return box

    def _info_val_lbl(self, grid, row, label_text) -> QLabel:
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #888; font-size: 10px; background: transparent;")
        val = QLabel("—")
        val.setStyleSheet("color: #CCCCCC; font-size: 10px; background: transparent;")
        grid.addWidget(lbl, row, 0)
        grid.addWidget(val, row, 1)
        return val

    @staticmethod
    def _lbl(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("color: #CCCCCC; font-size: 10px; background: transparent;")
        return l

    @staticmethod
    def _spinbox(mn, mx, val, step) -> QDoubleSpinBox:
        sb = QDoubleSpinBox()
        sb.setRange(mn, mx)
        sb.setValue(val)
        sb.setSingleStep(step)
        sb.setDecimals(2)
        sb.setStyleSheet(
            "QDoubleSpinBox { background: #2A2A3A; color: #00ffff; border: 1px solid #444; "
            "padding: 2px; border-radius: 3px; font-size: 10px; }"
        )
        return sb

    def _orientation_vector(self) -> tuple[float, float]:
        angle_rad = np.deg2rad(self._spin_orient.value())
        return float(np.cos(angle_rad)), float(np.sin(angle_rad))
    
    def _on_reset_params(self):
        self._spin_radius.blockSignals(True)
        self._spin_orient.blockSignals(True)
        self._spin_radius.setValue(_DEFAULT_RADIUS)
        self._spin_orient.setValue(_DEFAULT_ORIENT_DEG)
        self._spin_radius.blockSignals(False)
        self._spin_orient.blockSignals(False)
        self._recompute()

    def _on_prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._redraw()

    def _on_next_step(self):
        if self._current_step < len(self._steps) - 1:
            self._current_step += 1
            self._redraw()

    def _on_first_step(self):
        self._current_step = 0
        self._redraw()

    def _on_last_step(self):
        if self._steps:
            self._current_step = len(self._steps) - 1
            self._redraw()

    def _on_only_points(self):
        if self._steps:
            self._current_step = 0
            self._redraw(True, False, False)

    def _on_full_path(self):
        if self._steps:
            self._current_step = len(self._steps) - 1
            self._redraw(True, False, False)

    def _recompute(self):
        self._steps = self._generate_steps()
        self._current_step = 0
        self._redraw()

    def _generate_steps(self) -> list[_PathStep]:
        waypoints = list(_DEFAULT_WAYPOINTS)
        radius = self._spin_radius.value()
        orientation = self._orientation_vector()

        marked_states = list(waypoints)
        labels = [f"W{i + 1}" for i in range(len(waypoints))]
        bezier_points: list = []
        steps: list[_PathStep] = []

        end_pt = np.array(marked_states[0], dtype=float)
        i = 0
        lap_ms_len = len(marked_states)

        while True:
            if i == len(marked_states) - 1:
                break

            if lap_ms_len == len(marked_states):
                start_pt = end_pt.copy()
                end_pt = np.array(marked_states[i + 1], dtype=float)
            else:
                start_pt = np.array(marked_states[i], dtype=float)
                end_pt = np.array(marked_states[i + 1], dtype=float)
                lap_ms_len = len(marked_states)

            if i == 0:
                set_orient = np.array(orientation, dtype=float)
            else:
                set_orient = np.array(
                    self._algorithm.bezier_tangent(1.0, bezier_points[i - 1]),
                    dtype=float,
                )

            ti_vec = set_orient.copy()
            pi_vec = end_pt - start_pt
            ti_norm = np.linalg.norm(ti_vec)
            pi_norm = np.linalg.norm(pi_vec)

            if ti_norm == 0 or pi_norm == 0:
                break

            middle_point = start_pt + radius * (ti_vec / ti_norm)
            cos_a = np.clip(np.dot(ti_vec, pi_vec) / (ti_norm * pi_norm), -1.0, 1.0)
            angle = np.arccos(cos_a)

            completed_before = [list(c) for c in bezier_points]

            if angle < np.pi / 2:
                curve = [
                    tuple(start_pt.tolist()),
                    tuple(middle_point.tolist()),
                    tuple(end_pt.tolist()),
                ]
                step = _PathStep(
                    step_num=i,
                    start=start_pt.copy(),
                    end=end_pt.copy(),
                    ti_vec=ti_vec.copy(),
                    pi_vec=pi_vec.copy(),
                    middle_point=middle_point.copy(),
                    angle_deg=float(np.degrees(angle)),
                    is_uturn=False,
                    rotated_ti=None,
                    additional_point=None,
                    curve=curve,
                    completed_curves=completed_before,
                    all_waypoints=list(marked_states),
                    waypoint_labels=list(labels),
                )
                bezier_points.append(curve)
            else:
                cross = ti_vec[0] * pi_vec[1] - ti_vec[1] * pi_vec[0]
                rotated_ti = (
                    np.array([-ti_vec[1], ti_vec[0]])
                    if cross > 0
                    else np.array([ti_vec[1], -ti_vec[0]])
                )
                rot_norm = np.linalg.norm(rotated_ti)
                additional_point = start_pt + radius * 2.0 * (rotated_ti / rot_norm)
                curve = [
                    tuple(start_pt.tolist()),
                    tuple(middle_point.tolist()),
                    tuple(additional_point.tolist()),
                ]
                new_label = _midpoint_label(labels[i], labels[i + 1])
                marked_states.insert(i + 1, tuple(additional_point.tolist()))
                labels.insert(i + 1, new_label)
                step = _PathStep(
                    step_num=i,
                    start=start_pt.copy(),
                    end=end_pt.copy(),
                    ti_vec=ti_vec.copy(),
                    pi_vec=pi_vec.copy(),
                    middle_point=middle_point.copy(),
                    angle_deg=float(np.degrees(angle)),
                    is_uturn=True,
                    rotated_ti=rotated_ti.copy(),
                    additional_point=additional_point.copy(),
                    curve=curve,
                    completed_curves=completed_before,
                    all_waypoints=list(marked_states),
                    waypoint_labels=list(labels),
                )
                bezier_points.append(curve)

            steps.append(step)
            i += 1

        if steps:
            last_end = np.array(marked_states[-1], dtype=float)
            dummy_vec = np.array([1.0, 0.0])
            steps.append(_PathStep(
                step_num=i,
                start=last_end.copy(),
                end=last_end.copy(),
                ti_vec=dummy_vec,
                pi_vec=dummy_vec,
                middle_point=last_end.copy(),
                angle_deg=0.0,
                is_uturn=False,
                rotated_ti=None,
                additional_point=None,
                curve=[],
                completed_curves=[list(c) for c in bezier_points],
                all_waypoints=list(marked_states),
                waypoint_labels=list(labels),
                is_final=True,
            ))

        return steps

    def _redraw(self, points = True, vectors = True, robot = True):
        self._ax.cla()
        self._style_axes()

        total = len(self._steps)

        if total == 0:
            self._step_label.setText("Step: — / —")
            self._update_info_panel(None)
            self._canvas.draw_idle()
            return

        step = self._steps[self._current_step]
        self._step_label.setText(f"Step: {self._current_step + 1} / {total}")
        self._update_info_panel(step)

        if points:
            self._draw_waypoints(step.all_waypoints, step.waypoint_labels)

        t_vals = np.linspace(0, 1, 80)
        radius = self._spin_radius.value()

        if step.is_final:
            for j, curve in enumerate(step.completed_curves):
                pts = np.array([self._bezier_pt(t, curve) for t in t_vals])
                self._ax.plot(pts[:, 0], pts[:, 1],
                              color="#AAAAAA", linewidth=2.5, zorder=3)
            # dest_circle = Circle(
            #     (float(step.start[0]), float(step.start[1])),
            #     radius,
            #     fill=False,
            #     edgecolor="#4466FF",
            #     linewidth=2.0,
            #     linestyle="-",
            #     zorder=5,
            # )
            # self._ax.add_patch(dest_circle)
            self._ax.set_title(
                f"Path Complete [{self._current_step + 1}/{total}]",
                color="#333333", fontsize=11,
            )
            self._canvas.draw_idle()
            return

        for curve in step.completed_curves:
            pts = np.array([self._bezier_pt(t, curve) for t in t_vals])
            self._ax.plot(pts[:, 0], pts[:, 1], color="#AAAAAA", linewidth=2.0, zorder=3)

        robot_circle = Circle(
            (float(step.start[0]), float(step.start[1])),
            radius,
            fill=False,
            edgecolor="#4466FF",
            linewidth=1.5,
            linestyle="-",
            zorder=4,
        )
        if robot:
            self._ax.add_patch(robot_circle)

        arrow_len = radius * 2.0
        ti_unit = step.ti_vec / np.linalg.norm(step.ti_vec)
        pi_unit = step.pi_vec / np.linalg.norm(step.pi_vec)

        if vectors:
            self._draw_arrow(step.start, ti_unit * arrow_len, "#00CC44", "Ti")
            self._draw_arrow(step.start, pi_unit * arrow_len, "#FF3333", "Pi")

            self._ax.scatter(
                float(step.middle_point[0]), float(step.middle_point[1]),
                color="#FFAA00", zorder=8, s=100, marker="x", linewidths=2.5,
            )
            ann_p1 = self._ax.annotate(
                "P1", (float(step.middle_point[0]), float(step.middle_point[1])),
                textcoords="offset points", xytext=(6, 6),
                color="#FFAA00", fontsize=9,
            )
            ann_p1.draggable(True)

            if step.is_uturn:
                rot_unit = step.rotated_ti / np.linalg.norm(step.rotated_ti)
                self._draw_arrow(step.start, rot_unit * arrow_len * 1.2, "#FF66FF", "Ti'")

                ap = step.additional_point
                # self._ax.scatter(float(ap[0]), float(ap[1]),
                #                  color="#FF66FF", zorder=8, s=120, marker="*")
                ann_ap = self._ax.annotate(
                    "add. pt", (float(ap[0]), float(ap[1])),
                    textcoords="offset points", xytext=(6, 6),
                    color="#00CCFF", fontsize=9,
                )
                ann_ap.draggable(True)
                ctrl = np.array([step.start, step.middle_point, ap])
                self._ax.plot(ctrl[:, 0], ctrl[:, 1], "--", color="#AAAAAA", linewidth=0.8, zorder=2)
                pts = np.array([self._bezier_pt(t, step.curve) for t in t_vals])
                self._ax.plot(pts[:, 0], pts[:, 1], color="#4466FF", linewidth=2.5, zorder=5,
                            label=f"Step {self._current_step + 1} (U-turn)")
            else:
                ctrl = np.array([step.start, step.middle_point, step.end])
                self._ax.plot(ctrl[:, 0], ctrl[:, 1], "--", color="#AAAAAA", linewidth=0.8, zorder=2)
                pts = np.array([self._bezier_pt(t, step.curve) for t in t_vals])
                self._ax.plot(pts[:, 0], pts[:, 1], color="#0088FF", linewidth=2.5, zorder=5,
                            label=f"Step {self._current_step + 1}")

        # self._ax.legend(loc="upper left", fontsize=8, facecolor="#EEEEEE", framealpha=0.8)
        self._ax.set_title(
            f"Path Creation — Step {self._current_step + 1}/{total}"
            + (" [U-turn]" if step.is_uturn else ""),
            color="#333333", fontsize=11,
        )
        if not robot:
            self._ax.set_title(
            f"Path Creation — Points sequence",
            color="#333333", fontsize=11,
        )
        self._canvas.draw_idle()

    def _draw_waypoints(self, waypoints, labels):
        for pt, lbl in zip(waypoints, labels):
            x, y = float(pt[0]), float(pt[1])
            self._ax.scatter(x, y, color="#00CCFF", zorder=6, s=60)
            ann = self._ax.annotate(
                lbl, (x, y),
                textcoords="offset points", xytext=(7, 7),
                color="#00CCFF", fontsize=9, fontweight="bold",
            )
            ann.draggable(True)

    def _draw_arrow(self, origin, vec, color, label):
        ox, oy = float(origin[0]), float(origin[1])
        dx, dy = float(vec[0]), float(vec[1])
        self._ax.annotate(
            "",
            xy=(ox + dx, oy + dy),
            xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=2.0),
            zorder=7,
        )
        ann = self._ax.annotate(
            label,
            xy=(ox + dx * 1.15, oy + dy * 1.15),
            color=color, fontsize=9, fontweight="bold",
            ha="center", va="center",
            annotation_clip=False,
            zorder=8,
        )
        ann.draggable(True)

    def _update_info_panel(self, step: Optional[_PathStep]):
        if step is None:
            self._info_type.setText("—")
            self._info_angle.setText("—")
            self._info_start.setText("—")
            self._info_end.setText("—")
            return
        if step.is_final:
            self._info_type.setText("Final")
            self._info_angle.setText("—")
            self._info_start.setText(f"({step.start[0]:.2f}, {step.start[1]:.2f})")
            self._info_end.setText("—")
            return
        self._info_type.setText("U-turn" if step.is_uturn else "Direct")
        self._info_angle.setText(f"{step.angle_deg:.1f}°")
        self._info_start.setText(f"({step.start[0]:.2f}, {step.start[1]:.2f})")
        dest = step.additional_point if step.is_uturn else step.end
        self._info_end.setText(f"({float(dest[0]):.2f}, {float(dest[1]):.2f})")

    @staticmethod
    def _bezier_pt(t: float, verts) -> np.ndarray:
        p0, p1, p2 = map(np.array, verts)
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

    def _style_axes(self):
        self._ax.set_facecolor("#FFFFFF")
        self._ax.tick_params(colors="#555")
        for spine in self._ax.spines.values():
            spine.set_edgecolor("#333")
        self._ax.grid(True, color="#DDDDDD", linewidth=0.5)
        self._ax.set_aspect("equal", adjustable="datalim")
        self._ax.set_xlabel("x", color="#666")
        self._ax.set_ylabel("y", color="#666")
