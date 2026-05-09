import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QDoubleSpinBox, QGroupBox, QGridLayout,
    QSplitter, QScrollArea, QTextEdit,
)
from PyQt5.QtCore import Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure

from control.CollisionSectorAlgorithm import CollisionSectorAlgorithm
from utils.StyleSheet import StyleSheet

_C1_COLOR = "#00AAFF"
_C2_COLOR = "#FF6B35"
_MIN_COLOR = "#FFDD00"
_BOUNDARY_COLOR = "#FF4136"
_SECTOR1_COLOR = "#00AAFF"
_SECTOR2_COLOR = "#FF6B35"

_POINT_LABELS = ["P0 (start)", "P1 (middle)", "P2 (end)"]


class SectorBoundaryTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._algo = CollisionSectorAlgorithm()

        self._curve1: list[tuple[float, float]] = [(1.0, 9.0), (5.0, 7.0), (9.0, 9.0)]
        self._curve2: list[tuple[float, float]] = [(1.0, 6.0), (5.0, 8.0), (9.0, 6.0)]

        self._pick_curve: int = -1   # 1 or 2
        self._pick_pt: int = -1      # 0,1,2
        self._pick_btns1: list[QPushButton] = []
        self._pick_btns2: list[QPushButton] = []

        self._expansion_steps: list[dict] = []
        self._sector1 = None
        self._sector2 = None

        self._build_ui()
        self._sync_spins()
        self._canvas.mpl_connect("button_press_event", self._on_canvas_click)
        self._redraw()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)

        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        self._fig = Figure(figsize=(7, 7), facecolor="#FFFFFF")
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("background: #FFFFFF;")

        toolbar = NavigationToolbar2QT(self._canvas, canvas_widget)
        toolbar.setStyleSheet("background: #2e2e2e; color: #b1b1b1;")

        canvas_layout.addWidget(toolbar)
        canvas_layout.addWidget(self._canvas)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(270)
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
        ctrl_layout.addWidget(self._build_curve_group(1, _C1_COLOR, self._curve1, self._pick_btns1))
        ctrl_layout.addWidget(self._build_curve_group(2, _C2_COLOR, self._curve2, self._pick_btns2))
        ctrl_layout.addWidget(self._build_actions_group())
        ctrl_layout.addWidget(self._build_log_group())
        ctrl_layout.addStretch(1)

        scroll.setWidget(ctrl_widget)

        splitter.addWidget(canvas_widget)
        splitter.addWidget(scroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        root.addWidget(splitter)

    def _build_params_group(self) -> QGroupBox:
        box = QGroupBox("Parameters")
        box.setStyleSheet(StyleSheet.QGroupBoxStatistics.value)
        grid = QGridLayout(box)
        grid.setSpacing(6)

        grid.addWidget(self._lbl("Radius r₁ = r₂"), 0, 0)
        self._spin_radius = self._spinbox(0.05, 10.0, 0.5, 0.1)
        self._spin_radius.valueChanged.connect(self._redraw)
        grid.addWidget(self._spin_radius, 0, 1)

        grid.addWidget(self._lbl("Emergency factor"), 1, 0)
        self._spin_factor = self._spinbox(1.0, 3.0, 1.1, 0.05)
        self._spin_factor.valueChanged.connect(self._redraw)
        grid.addWidget(self._spin_factor, 1, 1)

        return box

    def _build_curve_group(self, curve_num: int, color: str,
                            pts: list, pick_btns: list) -> QGroupBox:
        box = QGroupBox(f"Curve {curve_num}")
        box.setStyleSheet(StyleSheet.QGroupBoxStatistics.value)
        layout = QVBoxLayout(box)
        layout.setSpacing(4)

        spins_attr = f"_c{curve_num}_spins"
        setattr(self, spins_attr, [])
        spins = getattr(self, spins_attr)

        for i, label in enumerate(_POINT_LABELS):
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent;")
            row = QHBoxLayout(row_w)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(4)

            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"color: {color}; font-size: 10px; font-weight: bold; background: transparent;"
            )
            row.addWidget(lbl)
            row.addStretch(1)

            pick_btn = QPushButton("Pick")
            pick_btn.setFixedSize(44, 20)
            pick_btn.setCheckable(True)
            pick_btn.setStyleSheet(self._pick_btn_style(color))
            pick_btn.clicked.connect(
                lambda checked, cn=curve_num, pi=i: self._on_pick_clicked(cn, pi, checked)
            )
            pick_btns.append(pick_btn)
            row.addWidget(pick_btn)
            layout.addWidget(row_w)

            xy_w = QWidget()
            xy_w.setStyleSheet("background: transparent;")
            xy = QHBoxLayout(xy_w)
            xy.setContentsMargins(0, 0, 0, 0)
            xy.setSpacing(4)

            xy.addWidget(self._lbl("x:"))
            sx = self._spinbox(-99.0, 99.0, pts[i][0], 0.5)
            sx.valueChanged.connect(lambda _, cn=curve_num: self._on_spin_changed(cn))
            xy.addWidget(sx)

            xy.addWidget(self._lbl("y:"))
            sy = self._spinbox(-99.0, 99.0, pts[i][1], 0.5)
            sy.valueChanged.connect(lambda _, cn=curve_num: self._on_spin_changed(cn))
            xy.addWidget(sy)

            spins.append((sx, sy))
            layout.addWidget(xy_w)

        self._pick_status = QLabel("")
        self._pick_status.setStyleSheet(
            "color: #FFAA00; font-size: 10px; background: transparent;"
        )
        self._pick_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._pick_status)

        return box

    def _build_actions_group(self) -> QGroupBox:
        box = QGroupBox("Algorithm")
        box.setStyleSheet(StyleSheet.QGroupBoxStatistics.value)
        layout = QVBoxLayout(box)
        layout.setSpacing(6)

        btn_run = QPushButton("Find & Expand Sectors")
        btn_run.setStyleSheet(StyleSheet.QPushButton.value)
        btn_run.setFixedHeight(32)
        btn_run.clicked.connect(self._on_run)
        layout.addWidget(btn_run)

        btn_clear = QPushButton("Clear Results")
        btn_clear.setStyleSheet(StyleSheet.QPushButton.value)
        btn_clear.setFixedHeight(28)
        btn_clear.clicked.connect(self._on_clear_results)
        layout.addWidget(btn_clear)

        return box

    def _build_log_group(self) -> QGroupBox:
        box = QGroupBox("Expansion Log")
        box.setStyleSheet(StyleSheet.QGroupBoxStatistics.value)
        layout = QVBoxLayout(box)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(180)
        self._log.setStyleSheet(
            "QTextEdit { background: #1A1A2E; color: #CCCCCC; border: none; "
            "font-size: 9px; font-family: monospace; }"
        )
        layout.addWidget(self._log)
        return box

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

    @staticmethod
    def _pick_btn_style(color: str) -> str:
        return (
            f"QPushButton {{ background: #2A2A3A; color: {color}; border: 1px solid {color}55; "
            f"border-radius: 3px; font-size: 10px; }}"
            f"QPushButton:checked {{ background: {color}33; border: 1px solid {color}; }}"
            f"QPushButton:hover {{ background: {color}22; }}"
        )

    @staticmethod
    def _bezier_pt(t: float, verts) -> np.ndarray:
        p0, p1, p2 = map(np.array, verts)
        return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2

    def _sync_spins(self):
        for i, (sx, sy) in enumerate(self._c1_spins):
            sx.blockSignals(True); sy.blockSignals(True)
            sx.setValue(self._curve1[i][0]); sy.setValue(self._curve1[i][1])
            sx.blockSignals(False); sy.blockSignals(False)
        for i, (sx, sy) in enumerate(self._c2_spins):
            sx.blockSignals(True); sy.blockSignals(True)
            sx.setValue(self._curve2[i][0]); sy.setValue(self._curve2[i][1])
            sx.blockSignals(False); sy.blockSignals(False)

    def _on_canvas_click(self, event):
        if event.inaxes != self._ax or event.button != 1:
            return
        if self._pick_curve < 0:
            return
        x, y = event.xdata, event.ydata
        pts = self._curve1 if self._pick_curve == 1 else self._curve2
        spins = self._c1_spins if self._pick_curve == 1 else self._c2_spins
        pick_btns = self._pick_btns1 if self._pick_curve == 1 else self._pick_btns2

        pts[self._pick_pt] = (x, y)
        sx, sy = spins[self._pick_pt]
        sx.blockSignals(True); sy.blockSignals(True)
        sx.setValue(x); sy.setValue(y)
        sx.blockSignals(False); sy.blockSignals(False)

        pick_btns[self._pick_pt].setChecked(False)
        self._pick_curve = -1
        self._pick_pt = -1
        self._pick_status.setText("")
        self._on_clear_results()
        self._redraw()

    def _on_pick_clicked(self, curve_num: int, pt_idx: int, checked: bool):
        all_btns = self._pick_btns1 + self._pick_btns2
        for btn in all_btns:
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)

        if checked:
            btns = self._pick_btns1 if curve_num == 1 else self._pick_btns2
            btns[pt_idx].blockSignals(True)
            btns[pt_idx].setChecked(True)
            btns[pt_idx].blockSignals(False)
            self._pick_curve = curve_num
            self._pick_pt = pt_idx
            self._pick_status.setText(
                f"Click canvas → set C{curve_num} {_POINT_LABELS[pt_idx]}"
            )
        else:
            self._pick_curve = -1
            self._pick_pt = -1
            self._pick_status.setText("")

    def _on_spin_changed(self, curve_num: int):
        spins = self._c1_spins if curve_num == 1 else self._c2_spins
        pts = self._curve1 if curve_num == 1 else self._curve2
        for i, (sx, sy) in enumerate(spins):
            pts[i] = (sx.value(), sy.value())
        self._on_clear_results()
        self._redraw()

    def _on_run(self):
        self._expansion_steps.clear()
        self._sector1 = None
        self._sector2 = None
        self._log.clear()

        r = self._spin_radius.value()
        ef = self._spin_factor.value()
        R = r * 2 * ef

        verts1 = self._curve1
        verts2 = self._curve2

        grid_n = 200
        t_arr = np.linspace(0, 1, grid_n)
        v_arr = np.linspace(0, 1, grid_n)
        T, V = np.meshgrid(t_arr, v_arr)
        t_flat = T.flatten()
        v_flat = V.flatten()

        p0_1, p1_1, p2_1 = map(np.array, verts1)
        p0_2, p1_2, p2_2 = map(np.array, verts2)

        tf = t_flat[:, None]
        vf = v_flat[:, None]
        pts1 = (1-tf)**2 * p0_1 + 2*(1-tf)*tf * p1_1 + tf**2 * p2_1
        pts2 = (1-vf)**2 * p0_2 + 2*(1-vf)*vf * p1_2 + vf**2 * p2_2

        dist_sq = np.sum((pts1 - pts2)**2, axis=1)
        min_idx = int(np.argmin(dist_sq))
        t_star = float(t_flat[min_idx])
        v_star = float(v_flat[min_idx])
        min_dist = float(np.sqrt(dist_sq[min_idx]))

        self._log.append(
            f"Global min: t*={t_star:.4f}  v*={v_star:.4f}\n"
            f"Min distance={min_dist:.4f}  R={R:.4f}\n"
        )

        if min_dist >= R:
            self._log.append("Min distance ≥ R: curves do not collide. No sector to expand.")
            self._redraw()
            return

        steps = self._expand_with_trace(t_star, v_star, verts1, verts2, R)
        self._expansion_steps = steps

        if steps:
            final = steps[-1]
            tl = final["extremes"][1][0]
            tu = final["extremes"][1][1]
            vl = final["extremes"][2][0]
            vu = final["extremes"][2][1]
            self._sector1 = (tl, tu)
            self._sector2 = (vl, vu)
            self._log.append(
                f"\nFinal sectors:\n"
                f"  Bézier curve 1: t ∈ [{tl:.4f}, {tu:.4f}]\n"
                f"  Bézier curve 2: v ∈ [{vl:.4f}, {vu:.4f}]"
            )

        self._redraw()

    def _expand_with_trace(self, t_star: float, v_star: float, verts1, verts2, R: float) -> list:
        v1 = np.array(verts1)
        v2 = np.array(verts2)
        R_sq = R * R

        queue = [(1, t_star), (2, v_star)]
        checked = set()
        extremes = {1: [t_star, t_star], 2: [v_star, v_star]}

        steps = []
        point_counter = [0]
        found_points = []

        point_counter[0] += 1
        found_points.append((1, t_star, 0, str(point_counter[0])))
        point_counter[0] += 1
        found_points.append((2, v_star, 0, str(point_counter[0])))

        steps.append({
            "extremes": {1: list(extremes[1]), 2: list(extremes[2])},
            "found_points": list(found_points),
            "queue_len": len(queue),
        })

        idx = 0
        while idx < len(queue):
            curve_id, param = queue[idx]
            idx += 1

            key = (curve_id, round(param, 7))
            if key in checked:
                continue
            checked.add(key)

            curr_verts = v1 if curve_id == 1 else v2
            other_verts = v2 if curve_id == 1 else v1
            other_id = 2 if curve_id == 1 else 1

            p_fixed = (
                (1-param)**2 * curr_verts[0]
                + 2*(1-param)*param * curr_verts[1]
                + param**2 * curr_verts[2]
            )

            roots = self._algo.find_roots_quartic(p_fixed, other_verts, R)
            step_label = f"From C{curve_id}@{param:.3f}: roots on C{other_id}={[f'{r:.3f}' for r in roots]}"

            for r_other in roots:
                p_other = (
                    (1-r_other)**2 * other_verts[0]
                    + 2*(1-r_other)*r_other * other_verts[1]
                    + r_other**2 * other_verts[2]
                )
                r_back = self._algo.get_closest_t_to_point(p_other, curr_verts)
                p_back = (
                    (1-r_back)**2 * curr_verts[0]
                    + 2*(1-r_back)*r_back * curr_verts[1]
                    + r_back**2 * curr_verts[2]
                )
                dist_sq = np.sum((p_other - p_back)**2)

                if dist_sq <= R_sq + 1e-7:
                    expanded = False
                    if r_other < extremes[other_id][0]:
                        extremes[other_id][0] = r_other
                        expanded = True
                    if r_other > extremes[other_id][1]:
                        extremes[other_id][1] = r_other
                        expanded = True
                    if r_back < extremes[curve_id][0]:
                        extremes[curve_id][0] = r_back
                        expanded = True
                    if r_back > extremes[curve_id][1]:
                        extremes[curve_id][1] = r_back
                        expanded = True

                    if expanded:
                        queue.append((other_id, r_other))
                        queue.append((curve_id, r_back))

                        point_counter[0] += 1
                        found_points.append((other_id, r_other, idx, str(point_counter[0])))
                        point_counter[0] += 1
                        found_points.append((curve_id, r_back, idx, str(point_counter[0])))

                        steps.append({
                            "extremes": {1: list(extremes[1]), 2: list(extremes[2])},
                            "found_points": list(found_points),
                            "queue_len": len(queue),
                            "note": step_label,
                        })

            self._log.append(step_label)

        return steps

    def _on_clear_results(self):
        self._expansion_steps.clear()
        self._sector1 = None
        self._sector2 = None
        self._log.clear()

    def _redraw(self):
        self._ax.cla()
        self._style_axes()

        t_vals = np.linspace(0, 1, 200)

        for verts, color, label in [
            (self._curve1, _C1_COLOR, "Bézier curve 1"),
            (self._curve2, _C2_COLOR, "Bézier Curve 2"),
        ]:
            pts = np.array([self._bezier_pt(t, verts) for t in t_vals])
            self._ax.plot(pts[:, 0], pts[:, 1], color=color, linewidth=2.5,
                          label=label, zorder=2)
            cp = np.array(verts)
            self._ax.plot(cp[:, 0], cp[:, 1], "--", color="#AAAAAA", linewidth=0.8, zorder=1)
            self._ax.scatter(cp[0, 0], cp[0, 1], color=color, zorder=5, s=60)
            self._ax.scatter(cp[2, 0], cp[2, 1], color=color, zorder=5, s=60)
            self._ax.scatter(cp[1, 0], cp[1, 1], color=color, zorder=5, s=40, marker="x")

        if self._expansion_steps:
            last = self._expansion_steps[-1]
            all_pts = last["found_points"]

            MAX_PTS = 15
            if len(all_pts) > MAX_PTS:
                seeds = all_pts[:2]
                rest = all_pts[2:]
                step = max(1, len(rest) // (MAX_PTS - 2))
                shown = seeds + rest[::step]
                shown = shown[:MAX_PTS]
            else:
                shown = all_pts

            for (cid, param, _step, num_lbl) in shown:
                verts = self._curve1 if cid == 1 else self._curve2
                pt = self._bezier_pt(param, verts)
                pt_color = _C1_COLOR if cid == 1 else _C2_COLOR
                self._ax.scatter(pt[0], pt[1], color=pt_color, zorder=7, s=55,
                                 edgecolors="white", linewidths=0.8)
                self._ax.annotate(
                    num_lbl, (pt[0], pt[1]),
                    textcoords="offset points", xytext=(5, 5),
                    color="white", fontsize=8, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="#222222", ec="none", alpha=0.7),
                    zorder=8,
                )

            if self._sector1:
                tl, tu = self._sector1
                ts = np.linspace(tl, tu, 80)
                sector_pts = np.array([self._bezier_pt(t, self._curve1) for t in ts])
                self._ax.plot(sector_pts[:, 0], sector_pts[:, 1],
                              color=_SECTOR1_COLOR, linewidth=10, alpha=0.55,
                              solid_capstyle="round", zorder=4)
                self._ax.annotate(
                    f"Sector 1\nt∈[{tl:.2f},{tu:.2f}]",
                    self._bezier_pt((tl + tu) / 2, self._curve1),
                    textcoords="offset points", xytext=(-10, 14),
                    color=_SECTOR1_COLOR, fontsize=8, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", fc="#12121E", ec=_SECTOR1_COLOR,
                              alpha=0.9),
                    zorder=9,
                )

            if self._sector2:
                vl, vu = self._sector2
                vs = np.linspace(vl, vu, 80)
                sector_pts = np.array([self._bezier_pt(v, self._curve2) for v in vs])
                self._ax.plot(sector_pts[:, 0], sector_pts[:, 1],
                              color=_SECTOR2_COLOR, linewidth=10, alpha=0.55,
                              solid_capstyle="round", zorder=4)
                self._ax.annotate(
                    f"Sector 2\nv∈[{vl:.2f},{vu:.2f}]",
                    self._bezier_pt((vl + vu) / 2, self._curve2),
                    textcoords="offset points", xytext=(-10, -24),
                    color=_SECTOR2_COLOR, fontsize=8, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", fc="#12121E", ec=_SECTOR2_COLOR,
                              alpha=0.9),
                    zorder=9,
                )

        self._ax.legend(loc="upper right", fontsize=9,
                        facecolor="#1A1A2E", edgecolor="#444", labelcolor="white")
        self._canvas.draw_idle()

    def _style_axes(self):
        self._ax.set_facecolor("#FFFFFF")
        self._ax.tick_params(colors="#555")
        for spine in self._ax.spines.values():
            spine.set_edgecolor("#333")
        self._ax.grid(True, color="#DDDDDD", linewidth=0.5)
        self._ax.set_aspect("equal", adjustable="datalim")
        self._ax.set_xlabel("x", color="#666")
        self._ax.set_ylabel("y", color="#666")
        self._ax.set_title(
            "Sector Boundary Expansion", color="#333333", fontsize=11
        )
