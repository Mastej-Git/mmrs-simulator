import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QDoubleSpinBox, QGroupBox, QGridLayout, QListWidget,
    QListWidgetItem, QSplitter, QScrollArea,
)
from PyQt5.QtCore import Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure

from control.PathCreationAlgorithm import PathCreationAlgorithm
from utils.StyleSheetDark import StyleSheetDark
from utils.StyleSheetLight import StyleSheetLight

# _POINT_COLORS = ["#00ffff", "#FFAA00", "#FF6B35"]
_POINT_COLORS = ["#FFAA00", "#FFAA00", "#FFAA00"]
_POINT_LABELS = ["P0 (start)", "P1 (middle)", "P2 (end)"]

_CURVE_PALETTE = [
    "#00CC44", "#00AAFF", "#FF6B35", "#CC44CC",
    "#FF4444", "#44CCCC", "#CCCC00", "#FF88AA",
]


class BezierTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._algorithm = PathCreationAlgorithm()
        self._waypoints: list[tuple[float, float]] = []

        self._draft_pts: list[tuple[float, float] | None] = [(-10, 0), (0, 10), (10, 0)]
        # committed curves: each entry is [(x0,y0),(x1,y1),(x2,y2)]
        self._curves: list[list[tuple[float, float]]] = []
        self._pick_idx: int = -1  # -1 = not in pick mode

        self._build_ui()
        self._sync_spins_from_draft()
        self._connect_canvas()
        self._redraw()

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
        toolbar.setStyleSheet("background: #f5f5f5; color: #333333;")

        canvas_layout.addWidget(toolbar)
        canvas_layout.addWidget(self._canvas)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(260)
        scroll.setStyleSheet(
            "QScrollArea { background: #f5f5f5; border: none; }"
            "QScrollBar:vertical { width: 6px; background: #e0e0e0; }"
            "QScrollBar::handle:vertical { background: #aaaaaa; border-radius: 3px; }"
        )

        ctrl_widget = QWidget()
        ctrl_widget.setStyleSheet("background: #f5f5f5;")
        ctrl_layout = QVBoxLayout(ctrl_widget)
        ctrl_layout.setContentsMargins(10, 10, 10, 10)
        ctrl_layout.setSpacing(10)

        ctrl_layout.addWidget(self._build_params_group())
        ctrl_layout.addWidget(self._build_draft_group())
        ctrl_layout.addWidget(self._build_curves_list_group())
        ctrl_layout.addWidget(self._build_path_group())
        ctrl_layout.addStretch(1)

        scroll.setWidget(ctrl_widget)

        splitter.addWidget(canvas_widget)
        splitter.addWidget(scroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        root.addWidget(splitter)

    # -- sub-panels ---------------------------------------------------

    def _build_params_group(self) -> QGroupBox:
        box = QGroupBox("Path Parameters")
        box.setStyleSheet(StyleSheetLight.QGroupBoxStatistics.value)
        grid = QGridLayout(box)
        grid.setSpacing(6)

        grid.addWidget(self._lbl("Radius"), 0, 0)
        self._spin_radius = self._spinbox(0.1, 50.0, 1.0, 0.5)
        self._spin_radius.valueChanged.connect(self._redraw)
        grid.addWidget(self._spin_radius, 0, 1)

        grid.addWidget(self._lbl("Orient. (°)"), 1, 0)
        self._spin_orient = self._spinbox(-180.0, 180.0, 0.0, 15.0)
        self._spin_orient.valueChanged.connect(self._redraw)
        grid.addWidget(self._spin_orient, 1, 1)

        return box

    def _build_draft_group(self) -> QGroupBox:
        box = QGroupBox("Draft Bezier Curve")
        box.setStyleSheet(StyleSheetLight.QGroupBoxStatistics.value)
        layout = QVBoxLayout(box)
        layout.setSpacing(6)

        self._pt_spins: list[tuple[QDoubleSpinBox, QDoubleSpinBox]] = []
        self._pick_btns: list[QPushButton] = []

        for i, (color, label) in enumerate(zip(_POINT_COLORS, _POINT_LABELS)):
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent;")
            row = QHBoxLayout(row_w)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(4)

            pt_lbl = QLabel(label)
            pt_lbl.setStyleSheet(
                f"color: {color}; font-size: 11px; font-weight: bold; background: transparent;"
            )
            row.addWidget(pt_lbl)
            row.addStretch(1)

            pick_btn = QPushButton("Pick")
            pick_btn.setFixedSize(44, 22)
            pick_btn.setCheckable(True)
            pick_btn.setStyleSheet(self._pick_btn_style(color))
            pick_btn.clicked.connect(lambda checked, idx=i: self._on_pick_clicked(idx, checked))
            self._pick_btns.append(pick_btn)
            row.addWidget(pick_btn)

            layout.addWidget(row_w)

            xy_w = QWidget()
            xy_w.setStyleSheet("background: transparent;")
            xy = QHBoxLayout(xy_w)
            xy.setContentsMargins(0, 0, 0, 0)
            xy.setSpacing(4)

            xy.addWidget(self._lbl("x:"))
            sx = self._spinbox(-999.0, 999.0, 0.0, 1.0)
            sx.valueChanged.connect(self._on_draft_spin_changed)
            xy.addWidget(sx)

            xy.addWidget(self._lbl("y:"))
            sy = self._spinbox(-999.0, 999.0, 0.0, 1.0)
            sy.valueChanged.connect(self._on_draft_spin_changed)
            xy.addWidget(sy)

            self._pt_spins.append((sx, sy))
            layout.addWidget(xy_w)

        self._pick_status = QLabel("")
        self._pick_status.setStyleSheet(
            "color: #FFAA00; font-size: 10px; background: transparent;"
        )
        self._pick_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._pick_status)

        btn_add = QPushButton("Add Curve")
        btn_add.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_add.setFixedHeight(30)
        btn_add.clicked.connect(self._on_add_curve)
        layout.addWidget(btn_add)

        btn_clear_draft = QPushButton("Clear Draft")
        btn_clear_draft.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_clear_draft.setFixedHeight(30)
        btn_clear_draft.clicked.connect(self._on_clear_draft)
        layout.addWidget(btn_clear_draft)

        return box

    def _build_curves_list_group(self) -> QGroupBox:
        box = QGroupBox("Bezier Curves")
        box.setStyleSheet(StyleSheetLight.QGroupBoxStatistics.value)
        layout = QVBoxLayout(box)
        layout.setSpacing(6)

        self._curves_list = QListWidget()
        self._curves_list.setMaximumHeight(130)
        self._curves_list.setStyleSheet(
            "QListWidget { background: #ebebeb; color: #333333; border: none; font-size: 10px; }"
            "QListWidget::item:selected { background: #d0d0d0; }"
        )
        layout.addWidget(self._curves_list)

        row_w = QWidget()
        row_w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(row_w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        btn_remove = QPushButton("Remove Selected")
        btn_remove.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_remove.setFixedHeight(28)
        btn_remove.clicked.connect(self._on_remove_selected_curve)
        row.addWidget(btn_remove)

        btn_clear_all = QPushButton("Clear All")
        btn_clear_all.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_clear_all.setFixedHeight(28)
        btn_clear_all.clicked.connect(self._on_clear_all_curves)
        row.addWidget(btn_clear_all)

        layout.addWidget(row_w)
        return box

    def _build_path_group(self) -> QGroupBox:
        box = QGroupBox("Waypoint Path")
        box.setStyleSheet(StyleSheetLight.QGroupBoxStatistics.value)
        layout = QVBoxLayout(box)
        layout.setSpacing(6)

        btn_clear = QPushButton("Clear All")
        btn_clear.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_clear.setFixedHeight(30)
        btn_clear.clicked.connect(self._on_clear_waypoints)
        layout.addWidget(btn_clear)

        btn_undo = QPushButton("Undo Last")
        btn_undo.setStyleSheet(StyleSheetLight.QPushButton.value)
        btn_undo.setFixedHeight(30)
        btn_undo.clicked.connect(self._on_undo)
        layout.addWidget(btn_undo)

        self._point_list = QListWidget()
        self._point_list.setMaximumHeight(110)
        self._point_list.setStyleSheet(
            "QListWidget { background: #ebebeb; color: #333333; border: none; font-size: 10px; }"
            "QListWidget::item:selected { background: #d0d0d0; }"
        )
        layout.addWidget(self._point_list)

        hint = QLabel("Left-click canvas to add\nwaypoints (no pick mode).")
        hint.setStyleSheet("color: #666666; font-size: 10px; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        return box

    @staticmethod
    def _lbl(text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("color: #333333; font-size: 10px; background: transparent;")
        return l

    @staticmethod
    def _spinbox(mn, mx, val, step) -> QDoubleSpinBox:
        sb = QDoubleSpinBox()
        sb.setRange(mn, mx)
        sb.setValue(val)
        sb.setSingleStep(step)
        sb.setDecimals(2)
        sb.setStyleSheet(
            "QDoubleSpinBox { background: #e8e8e8; color: #00aaaa; border: 1px solid #aaaaaa; "
            "padding: 2px; border-radius: 3px; font-size: 10px; }"
        )
        return sb

    @staticmethod
    def _pick_btn_style(color: str) -> str:
        return (
            f"QPushButton {{ background: #e8e8e8; color: {color}; border: 1px solid {color}55; "
            f"border-radius: 3px; font-size: 10px; }}"
            f"QPushButton:checked {{ background: {color}33; border: 1px solid {color}; }}"
            f"QPushButton:hover {{ background: {color}22; }}"
        )

    def _orientation_vector(self) -> tuple[float, float]:
        angle_rad = np.deg2rad(self._spin_orient.value())
        return float(np.cos(angle_rad)), float(np.sin(angle_rad))

    def _sync_spins_from_draft(self):
        for i, (sx, sy) in enumerate(self._pt_spins):
            pt = self._draft_pts[i]
            sx.blockSignals(True)
            sy.blockSignals(True)
            sx.setValue(pt[0] if pt is not None else 0.0)
            sy.setValue(pt[1] if pt is not None else 0.0)
            sx.blockSignals(False)
            sy.blockSignals(False)

    def _update_curves_list(self):
        self._curves_list.clear()
        for i, curve in enumerate(self._curves):
            color = _CURVE_PALETTE[i % len(_CURVE_PALETTE)]
            p0, p1, p2 = curve
            item = QListWidgetItem(
                f"C{i}  ({p0[0]:.1f},{p0[1]:.1f}) → ({p2[0]:.1f},{p2[1]:.1f})"
            )
            item.setForeground(__import__("PyQt5.QtGui", fromlist=["QColor"]).QColor(color))
            self._curves_list.addItem(item)

    def _connect_canvas(self):
        self._canvas.mpl_connect("button_press_event", self._on_canvas_click)

    def _on_canvas_click(self, event):
        if event.inaxes != self._ax or event.button != 1:
            return

        if self._pick_idx >= 0:
            x, y = event.xdata, event.ydata
            self._draft_pts[self._pick_idx] = (x, y)
            sx, sy = self._pt_spins[self._pick_idx]
            sx.blockSignals(True)
            sy.blockSignals(True)
            sx.setValue(x)
            sy.setValue(y)
            sx.blockSignals(False)
            sy.blockSignals(False)
            self._pick_btns[self._pick_idx].setChecked(False)
            self._pick_idx = -1
            self._pick_status.setText("")
            self._redraw()
        else:
            self._waypoints.append((event.xdata, event.ydata))
            self._update_point_list()
            self._redraw()

    def _on_pick_clicked(self, idx: int, checked: bool):
        for i, btn in enumerate(self._pick_btns):
            if i != idx:
                btn.blockSignals(True)
                btn.setChecked(False)
                btn.blockSignals(False)

        if checked:
            self._pick_idx = idx
            self._pick_status.setText(f"Click canvas → set {_POINT_LABELS[idx]}")
        else:
            self._pick_idx = -1
            self._pick_status.setText("")

    def _on_draft_spin_changed(self):
        for i, (sx, sy) in enumerate(self._pt_spins):
            self._draft_pts[i] = (sx.value(), sy.value())
        self._redraw()

    def _on_add_curve(self):
        if any(p is None for p in self._draft_pts):
            return
        self._curves.append([tuple(p) for p in self._draft_pts])
        self._update_curves_list()
        self._redraw()

    def _on_clear_draft(self):
        self._draft_pts = [None, None, None]
        self._pick_idx = -1
        self._pick_status.setText("")
        for btn in self._pick_btns:
            btn.setChecked(False)
        for sx, sy in self._pt_spins:
            sx.blockSignals(True)
            sy.blockSignals(True)
            sx.setValue(0.0)
            sy.setValue(0.0)
            sx.blockSignals(False)
            sy.blockSignals(False)
        self._redraw()

    def _on_remove_selected_curve(self):
        row = self._curves_list.currentRow()
        if row < 0 or row >= len(self._curves):
            return
        self._curves.pop(row)
        self._update_curves_list()
        self._redraw()

    def _on_clear_all_curves(self):
        self._curves.clear()
        self._update_curves_list()
        self._redraw()

    def _on_clear_waypoints(self):
        self._waypoints.clear()
        self._update_point_list()
        self._redraw()

    def _on_undo(self):
        if self._waypoints:
            self._waypoints.pop()
            self._update_point_list()
            self._redraw()

    def _update_point_list(self):
        self._point_list.clear()
        for i, (x, y) in enumerate(self._waypoints):
            self._point_list.addItem(QListWidgetItem(f"P{i}  ({x:.2f}, {y:.2f})"))

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _redraw(self):
        self._ax.cla()
        self._style_axes()

        if self._waypoints:
            xs, ys = zip(*self._waypoints)
            self._ax.scatter(xs, ys, color="#00ffff", zorder=5, s=40)
            for i, (x, y) in enumerate(self._waypoints):
                self._ax.annotate(
                    f"W{i}", (x, y),
                    textcoords="offset points", xytext=(5, 5),
                    color="#AAAAAA", fontsize=8,
                )

        if len(self._waypoints) >= 2:
            self._draw_path_curves()

        self._draw_all_bezier_curves()

        self._canvas.draw_idle()

    def _draw_path_curves(self):
        radius = self._spin_radius.value()
        orientation = self._orientation_vector()
        waypoints = [tuple(map(float, p)) for p in self._waypoints]
        try:
            segments = self._algorithm.create_path(list(waypoints), orientation, radius)
        except Exception:
            return

        t_vals = np.linspace(0, 1, 60)
        for seg in segments:
            pts = np.array([self._bezier_pt(t, seg) for t in t_vals])
            self._ax.plot(pts[:, 0], pts[:, 1], color="#FF6B35", linewidth=2)
            cp = np.array(seg)
            self._ax.plot(cp[:, 0], cp[:, 1], "--", color="#555555", linewidth=0.8)
            self._ax.scatter(cp[1, 0], cp[1, 1], color="#FFAA00", zorder=4, s=25, marker="x")

    def _draw_all_bezier_curves(self):
        t_vals = np.linspace(0, 1, 100)

        for i, curve in enumerate(self._curves):
            color = _CURVE_PALETTE[i % len(_CURVE_PALETTE)]
            p0, p1, p2 = curve
            cp = np.array([p0, p1, p2])
            self._ax.plot(cp[:, 0], cp[:, 1], "--", color="#AAAAAA", linewidth=0.8)
            pts = np.array([self._bezier_pt(t, [p0, p1, p2]) for t in t_vals])
            self._ax.plot(pts[:, 0], pts[:, 1], color=color, linewidth=2.5,
                          label=f"C{i}")
            for pt, lbl in zip([p0, p2], [f"C{i} start", f"C{i} end"]):
                self._ax.scatter(pt[0], pt[1], color=color, zorder=7, s=50)
            self._ax.scatter(p1[0], p1[1], color=color, zorder=7, s=30, marker="x")

        defined = [p for p in self._draft_pts if p is not None]
        for i, pt in enumerate(self._draft_pts):
            if pt is None:
                continue
            self._ax.scatter(pt[0], pt[1], color=_POINT_COLORS[i], zorder=8, s=70, alpha=0.7)
            self._ax.annotate(
                _POINT_LABELS[i], pt,
                textcoords="offset points", xytext=(6, 6),
                color=_POINT_COLORS[i], fontsize=8, alpha=0.9,
            )

        if len(defined) == 3:
            p0, p1, p2 = self._draft_pts
            cp = np.array([p0, p1, p2])
            self._ax.plot(cp[:, 0], cp[:, 1], "--", color="#AAAAAA", linewidth=0.8)
            pts = np.array([self._bezier_pt(t, [p0, p1, p2]) for t in t_vals])
            self._ax.plot(pts[:, 0], pts[:, 1], color="#FFAA00", linewidth=2,
                          linestyle="--", label="draft")

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
        self._ax.set_title("Bezier Curve Viewer", color="#333333", fontsize=11)
