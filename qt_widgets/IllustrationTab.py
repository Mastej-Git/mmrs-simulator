import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle


_BG       = "#FFFFFF"
_PANEL_BG = "#FFFFFF"
_GREEN    = "#2E9E5B"
_PINK     = "#D95050"
_GREEN_EC = "#1B6B3A"
_PINK_EC  = "#A03030"
_ARROW    = "#444444"
_DOTTED   = "#CCCCCC"
_TEXT     = "#222222"
_GRID     = "#EEEEEE"

_ROBOT_R = 0.55


# ── spec dataclasses ───────────────────────────────────────────────────────────

@dataclass
class TrajectorySpec:
    """Quadratic Bezier path with direction arrows at given fractions (0-1)."""

    p0: Sequence[float]
    ctrl: Sequence[float]
    p2: Sequence[float]
    arrow_fracs: List[float] = field(default_factory=lambda: [0.5])
    color: str = _ARROW
    lw: float = 1.8


@dataclass
class RobotSpec:
    """A robot rendered as a filled disk."""

    pos: Sequence[float]  # (x, y)
    color: str = _GREEN
    edge_color: str = _GREEN_EC
    alpha: float = 1.0
    zorder: int = 3


@dataclass
class DeadlockArrowSpec:
    """Arrow pointing from robots[from_idx] toward robots[to_idx]."""

    from_idx: int
    to_idx: int


# ── helpers ────────────────────────────────────────────────────────────────────

def trajectory_point(spec: TrajectorySpec, t: float) -> tuple:
    """Return (x, y) on the bezier trajectory at parameter t ∈ [0, 1]."""
    p0  = np.asarray(spec.p0,   dtype=float)
    p1  = np.asarray(spec.ctrl, dtype=float)
    p2  = np.asarray(spec.p2,   dtype=float)
    pt  = (1 - t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2
    return (float(pt[0]), float(pt[1]))


# ── default scenes ─────────────────────────────────────────────────────────────

_DEFAULT_COLLISION_TRAJECTORIES: List[TrajectorySpec] = [
    TrajectorySpec(
        p0=(-3.2, -2.8), ctrl=(0.5, -0.3), p2=(2.0, 3.0),
        arrow_fracs=[0.2, 0.72],
    ),
    TrajectorySpec(
        p0=(-3.0, 0.2), ctrl=(-0.5, 1.0), p2=(3.2, 2.2),
        arrow_fracs=[0.18, 0.75],
    ),
]

# Robots placed at t=0.55 on traj-1 and t=0.5 on traj-2 → overlap (collision)
_DEFAULT_COLLISION_ROBOTS: List[RobotSpec] = [
    RobotSpec(
        pos=trajectory_point(_DEFAULT_COLLISION_TRAJECTORIES[0], 0.55),
        color=_GREEN, edge_color=_GREEN_EC, zorder=3,
    ),
    RobotSpec(
        pos=trajectory_point(_DEFAULT_COLLISION_TRAJECTORIES[1], 0.50),
        color=_PINK, edge_color=_PINK_EC, zorder=4,
    ),
]

_DEFAULT_DEADLOCK_ROBOTS: List[RobotSpec] = [
    RobotSpec(pos=( 1.79,  2.0)),  # Traj0 ∩ Traj1
    RobotSpec(pos=(-1.79,  2.0)),  # Traj0 ∩ Traj2
    RobotSpec(pos=( 0.0,  -0.9)),  # Traj1 ∩ Traj2
]

# Each robot's trajectory: comes from its road, curves toward the next robot
_DEFAULT_DEADLOCK_TRAJECTORIES: List[TrajectorySpec] = [
    TrajectorySpec(
        p0=(-4.0, 2.0), ctrl=(0.0, 2.0), p2=(4.0, 2.0),
        arrow_fracs=[0.15, 0.5, 0.9],
    ),
    TrajectorySpec(
        p0=(3.0, 4.0), ctrl=(0.0, -1.0), p2=(-2.0, -4.0),
        arrow_fracs=[0.1, 0.45, 0.9],
    ),
    TrajectorySpec(
        p0=(2.0, -4.0), ctrl=(0.0, -1.0), p2=(-3.0, 4.0),
        arrow_fracs=[0.2, 0.6, 0.9],
    ),
]

_DEFAULT_DEADLOCK_ARROWS: List[DeadlockArrowSpec] = [
    DeadlockArrowSpec(0, 2),
    DeadlockArrowSpec(1, 0),
    DeadlockArrowSpec(2, 1),
]


# ── drawing helpers ────────────────────────────────────────────────────────────

def _bezier(p0, p1, p2, n=120):
    t = np.linspace(0, 1, n)
    x = (1 - t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
    y = (1 - t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
    return x, y


def _draw_trajectory(ax, xs, ys, color, fracs, lw):
    ax.plot(xs, ys, color=color, lw=lw, zorder=2)
    for frac in fracs:
        idx = int(len(xs) * frac)
        dx = xs[idx + 1] - xs[idx - 1]
        dy = ys[idx + 1] - ys[idx - 1]
        ax.annotate(
            "",
            xy=(xs[idx] + dx * 0.001, ys[idx] + dy * 0.001),
            xytext=(xs[idx] - dx * 0.5, ys[idx] - dy * 0.5),
            arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=12),
            zorder=5,
        )


def _style_ax(ax, xlim, ylim):
    ax.set_facecolor(_PANEL_BG)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.set_axisbelow(True)
    ax.grid(True, color=_GRID, linewidth=1)
    for spine in ax.spines.values():
        spine.set_edgecolor("#CCCCCC")
        spine.set_linewidth(0.8)


# ── panel drawing ──────────────────────────────────────────────────────────────

def _draw_collision(ax, trajectories: List[TrajectorySpec], robots: List[RobotSpec]):
    _style_ax(ax, (-3.5, 3.5), (-3.5, 3.5))

    for traj in trajectories:
        xs, ys = _bezier(traj.p0, traj.ctrl, traj.p2)
        _draw_trajectory(ax, xs, ys, traj.color, traj.arrow_fracs, traj.lw)

    for robot in robots:
        ax.add_patch(
            Circle(
                robot.pos, _ROBOT_R,
                color=robot.color, ec=robot.edge_color,
                lw=1.5, alpha=robot.alpha, zorder=robot.zorder,
            )
        )

    ax.set_title("Collision", color=_TEXT, fontsize=11, pad=6)


def _draw_deadlock(
    ax,
    robots: List[RobotSpec],
    arrows: Optional[List[DeadlockArrowSpec]] = None,
    trajectories: Optional[List[TrajectorySpec]] = None,
):
    _style_ax(ax, (-4, 4), (-4, 4))

    # dash = dict(color=_DOTTED, lw=1.0, ls="--", zorder=1)
    # ax.plot([-4, 4], [0, 0], **dash)
    # ax.plot([0, 0], [-4, 4], **dash)
    # ax.plot([0, 4], [0, 4], **dash)

    if trajectories:
        for traj in trajectories:
            xs, ys = _bezier(traj.p0, traj.ctrl, traj.p2)
            _draw_trajectory(ax, xs, ys, traj.color, traj.arrow_fracs, traj.lw)

    positions = [np.asarray(r.pos, dtype=float) for r in robots]

    for robot in robots:
        ax.add_patch(
            Circle(
                robot.pos, _ROBOT_R,
                color=robot.color, ec=robot.edge_color,
                lw=1.5, alpha=robot.alpha, zorder=robot.zorder,
            )
        )

    if arrows is None:
        arrows = [DeadlockArrowSpec(i, (i + 1) % len(robots)) for i in range(len(robots))]

    for arrow in arrows:
        src = positions[arrow.from_idx]
        dst = positions[arrow.to_idx]
        direction = dst - src
        direction = direction / np.linalg.norm(direction)
        ax.annotate(
            "",
            xy=src + direction * (_ROBOT_R * 0.7),
            xytext=src - direction * (_ROBOT_R * 0.7),
            arrowprops=dict(arrowstyle="-|>", color=_ARROW, lw=1.8, mutation_scale=12),
            zorder=6,
        )

    ax.set_title("Deadlock", color=_TEXT, fontsize=11, pad=6)


# ── widget ─────────────────────────────────────────────────────────────────────


class IllustrationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._fig = Figure(figsize=(9, 4.5), facecolor=_BG)
        self._fig.subplots_adjust(left=0.04, right=0.96, wspace=0.12)
        self._ax_col, self._ax_dead = self._fig.subplots(1, 2)

        self._canvas = FigureCanvas(self._fig)
        self._canvas.setStyleSheet("background: #FFFFFF;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

        self.draw_collision(_DEFAULT_COLLISION_TRAJECTORIES, _DEFAULT_COLLISION_ROBOTS)
        self.draw_deadlock(
            _DEFAULT_DEADLOCK_ROBOTS,
            _DEFAULT_DEADLOCK_ARROWS,
            _DEFAULT_DEADLOCK_TRAJECTORIES,
        )

    def draw_collision(
        self, trajectories: List[TrajectorySpec], robots: List[RobotSpec]
    ) -> None:
        """Redraw the collision panel with the given trajectories and robot disks."""
        self._ax_col.clear()
        _draw_collision(self._ax_col, trajectories, robots)
        self._canvas.draw()

    def draw_deadlock(
        self,
        robots: List[RobotSpec],
        arrows: Optional[List[DeadlockArrowSpec]] = None,
        trajectories: Optional[List[TrajectorySpec]] = None,
    ) -> None:
        """Redraw the deadlock panel. arrows=None → automatic cycle; trajectories=None → roads only."""
        self._ax_dead.clear()
        _draw_deadlock(self._ax_dead, robots, arrows, trajectories)
        self._canvas.draw()
