import numpy as np
from typing import List
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


_BG        = "#FFFFFF"
_GRID      = "#EEEEEE"
_TEXT      = "#222222"
_CURVE     = "#2196F3"   # Bezier curve
_CTRL_POLY = "#BBBBBB"   # control polygon
_CTRL_PT   = "#444444"   # P control points
_LVL1      = "#FF9800"   # first interpolation   (Q)

_LVL3      = "#2ECC71"   # point on curve B(t)
_PICK_R    = 0.4         # drag pick radius in data coords


class DeCasteljauTab(QWidget):

    _DEFAULT_CTRL = np.array([
        [-3.0, -1.0],
        [ 0.0,  2.0],
        [ 3.0, -1.0],
    ], dtype=float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ctrl     = self._DEFAULT_CTRL.copy()
        self._t        = 0.5
        self._drag_idx = None
        self._build_ui()
        self._redraw()

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(4)

        self._fig    = Figure(facecolor=_BG)
        self._ax     = self._fig.add_subplot(111)
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("background: #FFFFFF;")
        root.addWidget(self._canvas, stretch=1)

        # for event, handler in [
        #     ("button_press_event",   self._on_press),
        #     ("motion_notify_event",  self._on_motion),
        #     ("button_release_event", self._on_release),
        # ]:
        #     self._canvas.mpl_connect(event, handler)

        row = QHBoxLayout()
        row.setContentsMargins(4, 2, 4, 2)

        lbl_t = QLabel("t")
        lbl_t.setStyleSheet("color:#333; font-size:13px; font-weight:bold;")
        row.addWidget(lbl_t)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 1000)
        self._slider.setValue(500)
        self._slider.valueChanged.connect(self._on_slider)
        row.addWidget(self._slider, stretch=1)

        self._val_lbl = QLabel("0.500")
        self._val_lbl.setStyleSheet("color:#333; font-size:13px; min-width:44px;")
        row.addWidget(self._val_lbl)

        root.addLayout(row)

    # ── interaction ────────────────────────────────────────────────────────────

    def _on_slider(self, value: int):
        self._t = value / 1000.0
        self._val_lbl.setText(f"{self._t:.3f}")
        self._redraw()

    def _on_press(self, event):
        if event.inaxes != self._ax or event.button != 1:
            return
        click = np.array([event.xdata, event.ydata])
        dists = np.linalg.norm(self._ctrl - click, axis=1)
        idx   = int(np.argmin(dists))
        if dists[idx] < _PICK_R:
            self._drag_idx = idx

    def _on_motion(self, event):
        if self._drag_idx is None or event.inaxes != self._ax:
            return
        self._ctrl[self._drag_idx] = [event.xdata, event.ydata]
        self._redraw()

    def _on_release(self, _event):
        self._drag_idx = None

    # ── de Casteljau ───────────────────────────────────────────────────────────

    @staticmethod
    def _casteljau_levels(pts: np.ndarray, t: float) -> List[np.ndarray]:
        """Return every level of the de Casteljau pyramid for parameter t."""
        levels = [pts.copy()]
        while len(levels[-1]) > 1:
            prev = levels[-1]
            levels.append((1 - t) * prev[:-1] + t * prev[1:])
        return levels

    # ── drawing ────────────────────────────────────────────────────────────────

    def _redraw(self):
        ax = self._ax
        ax.cla()
        self._style_ax()
        t = self._t

        # Full Bezier curve
        ts    = np.linspace(0, 1, 300)
        curve = np.vstack([self._casteljau_levels(self._ctrl, ti)[-1] for ti in ts])
        ax.plot(curve[:, 0], curve[:, 1],
                color=_CURVE, lw=2.5, zorder=2, solid_capstyle="round")

        # Control polygon
        ax.plot(self._ctrl[:, 0], self._ctrl[:, 1],
                ls="--", color=_CTRL_POLY, lw=1.2, zorder=1)

        # de Casteljau pyramid at current t
        levels   = self._casteljau_levels(self._ctrl, t)
        colors   = [_CTRL_PT, _LVL1]
        prefixes = ["P",      "Q"]

        for lvl_i, (pts, color, prefix) in enumerate(
            zip(levels[:-1], colors, prefixes)
        ):
            if lvl_i > 0:
                ax.plot(pts[:, 0], pts[:, 1], color=color, lw=1.6, zorder=3)
            for i, pt in enumerate(pts):
                ax.scatter(*pt, color=color, s=58, zorder=6, clip_on=False)
                p = ax.annotate(
                    f"$\\mathit{{{prefix}}}_{i}$", pt,
                    textcoords="offset points", xytext=(6, 5),
                    color=color, fontsize=10, fontweight="bold", zorder=7,
                )
                p.draggable(True)

        b = levels[-1][0]
        ax.scatter(*b, color=_LVL3, s=130, zorder=8, marker="*", clip_on=False)
        pb = ax.annotate(
            r"$\mathbf{B}(t)$", b,
            textcoords="offset points", xytext=(8, 5),
            color=_LVL3, fontsize=11, fontweight="bold", zorder=9,
        )
        pb.draggable(True)

        ax.set_title(f"de Casteljau algorithm  —  t = {t:.3f}",
                     color=_TEXT, fontsize=12, pad=8)
        self._canvas.draw_idle()

    def _style_ax(self):
        self._ax.set_facecolor(_BG)
        self._ax.set_xlim(-4, 4)
        self._ax.set_ylim(-3, 4)
        self._ax.set_aspect("equal", adjustable="datalim")
        self._ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        self._ax.set_axisbelow(True)
        self._ax.grid(True, color=_GRID, linewidth=0.8)
        for spine in self._ax.spines.values():
            spine.set_edgecolor("#CCCCCC")
            spine.set_linewidth(0.8)
