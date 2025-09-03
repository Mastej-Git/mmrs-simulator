from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QTabWidget, 
    QWidget, 
    QVBoxLayout, 
    QFrame
)
from PyQt5.QtCore import QTimer, Qt
from StyleSheet import StyleSheet

import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches

import random


class MplCanvas(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)

        self.draw_square_grid(10)
        self.draw_bezier_curve()

    def draw_square_grid(self, size=10):
        for x in range(size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.set_xlim(0, size)
        self.ax.set_ylim(0, size)
        self.ax.set_aspect("equal")

    def draw_bezier_curve(self):
        verts = [
            (1, 1),
            (2, 3),
            (4, 3),
            (5, 1)
        ]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        path = Path(verts, codes)

        patch = patches.PathPatch(path, facecolor="none", lw=2, edgecolor="blue")
        self.ax.add_patch(patch)

        # Plot control points
        x, y = zip(*verts)
        self.ax.plot(x, y, "ro--")


class Snake(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = figure.add_subplot(111)
        super().__init__(figure)

        self.game_over = False
        self.is_food = True
        self.board_size = 30
        self.head_pos = [3, 1]
        self.food_pos = [5, 5]
        self.direction = "RIGHT"
        
        self.square_head = patches.Rectangle(
            (self.head_pos[0], self.head_pos[1]),
            1, 1,
            facecolor="blue",
            edgecolor="black",
            linewidth=0.5
        )

        self.square_body1 = patches.Rectangle(
            (self.head_pos[0] - 1, self.head_pos[1]),
            1, 1,
            facecolor="blue",
            edgecolor="black",
            linewidth=0.5
        )

        self.square_body2 = patches.Rectangle(
            (self.head_pos[0] - 2, self.head_pos[1]),
            1, 1,
            facecolor="blue",
            edgecolor="black",
            linewidth=0.5
        )

        self.body = [self.square_body1, self.square_body2]

        self.square_food = patches.Rectangle(
            (self.food_pos[0], self.food_pos[1]),
            1, 1,
            facecolor="red",
            edgecolor="black",
            linewidth=0.5
        )

        for x in range(self.board_size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.add_patch(self.square_head)
        for patch in self.body:
            self.ax.add_patch(patch)
        self.ax.add_patch(self.square_food)
        self.ax.set_xlim(0, self.board_size)
        self.ax.set_ylim(0, self.board_size)
        self.ax.set_aspect("equal")
        # self.ax.set_position([0, 0, 1, 1])
        # self.ax.axis("off")


        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # self.move_rectangle(square)

    def start_moving(self):
        self.timer.start(100)

    def update_direction(self):
        if self.direction == "RIGHT":
            self.head_pos[0] += 1
        elif self.direction == "DOWN":
            self.head_pos[1] -= 1
        elif self.direction == "LEFT":
            self.head_pos[0] -= 1
        elif self.direction == "UP":
            self.head_pos[1] += 1

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_D and self.direction != "LEFT":
            self.direction = "RIGHT"
        elif event.key() == Qt.Key_S and self.direction != "UP":
            self.direction = "DOWN"
        elif event.key() == Qt.Key_A and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif event.key() == Qt.Key_W and self.direction != "DOWN":
            self.direction = "UP"

    def spawn_food(self):
        if not self.is_food:
            self.food_pos = [random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)]
            self.is_food = True
            # self.body.insert(0, self.head_pos)

    def check_collision(self):
        if self.head_pos[0] == self.food_pos[0] and self.head_pos[1] == self.food_pos[1]:
            self.is_food = False
            return True
        return False

    def update_position(self):
        if not self.game_over:
            old_head_pos = self.square_head.get_xy()
            self.update_direction()
            # if self.check_collision():
            #     self.spawn_food()
            tail_pos = self.body[len(self.body) - 1].get_xy()
            self.square_head.set_xy((self.head_pos[0], self.head_pos[1]))
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i].set_xy((self.body[i - 1].get_x(), self.body[i - 1].get_y()))
            self.body[0].set_xy(old_head_pos)
            if self.check_collision():
                new_tail = patches.Rectangle(
                        (tail_pos[0], tail_pos[1]),
                        1, 1,
                        facecolor="blue",
                        edgecolor="black",
                        linewidth=0.5
                    )
                self.body.append(new_tail)
                self.ax.add_patch(new_tail)
                self.spawn_food()
            self.square_food.set_xy((self.food_pos[0], self.food_pos[1]))
            self.draw()
        else:
            self.timer.stop()


class RobotSimulation(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = figure.add_subplot(111)
        super().__init__(figure)

        self.board_size = 15
        self.position_idxs = [1, 1, 1]
        self.forbidden_positions = [(0, 0), (1, 1), (3, 3)]
        
        self.robot1 = patches.Rectangle(
            (0, 0),
            1, 1,
            facecolor="red",
            edgecolor="black",
            linewidth=0.5
        )

        self.robot2 = patches.Rectangle(
            (1, 1),
            1, 1,
            facecolor="green",
            edgecolor="black",
            linewidth=0.5
        )

        self.robot3 = patches.Rectangle(
            (3, 3),
            1, 1,
            facecolor="#751d16",
            edgecolor="black",
            linewidth=0.5
        )

        self.positions1 = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
            (4, 1), (4, 2), (4, 3), (4, 4),
            (3, 4), (2, 4), (1, 4), (0, 4),
            (0, 3), (0, 2), (0, 1)
        ]

        self.positions2 = [
            (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),
            (11, 1), (12, 1), (13, 1),
            (13, 2), (13, 3), (13, 4), (13, 5), (13, 6),
            (13, 7), (13, 8), (13, 9), (13, 10), (13, 11),
            (13, 12), (13, 13),
            (12, 13), (11, 13), (10, 13), (9, 13), (8, 13),
            (7, 13), (6, 13), (5, 13), (4, 13), (3, 13),
            (2, 13), (1, 13),
            (1, 12), (1, 11), (1, 10), (1, 9), (1, 8),
            (1, 7), (1, 6), (1, 5), (1, 4), (1, 3),
            (1, 2)
        ]

        self.positions3 = [
            (3, 3), (4, 3), (5, 3),
            (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
            (5, 9), (5, 10), (5, 11), (5, 12),
            (4, 12), (3, 12),
            (3, 11), (3, 10), (3, 9), (3, 8), (3, 7),
            (3, 6), (3, 5), (3, 4)
        ]

        for x in range(self.board_size + 1):
            self.ax.axhline(x, color="gray", linewidth=0.5)
            self.ax.axvline(x, color="gray", linewidth=0.5)

        self.ax.add_patch(self.robot1)
        self.ax.add_patch(self.robot2)
        self.ax.add_patch(self.robot3)

        self.ax.set_xlim(0, self.board_size)
        self.ax.set_ylim(0, self.board_size)
        self.ax.set_aspect("equal")
        # self.ax.set_position([0, 0, 1, 1])
        # self.ax.axis("off")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

    def start_moving(self) -> None:
        self.timer.start(200)

    def update_position(self) -> None:
        # for i in range(len(self.position_idxs)):
        #     self.position_idxs[i] += 1
        if self.position_idxs[0] == len(self.positions1):
            self.position_idxs[0] = 0
        if self.position_idxs[1] == len(self.positions2):
            self.position_idxs[1] = 0
        if self.position_idxs[2] == len(self.positions3):
            self.position_idxs[2] = 0
        if (self.positions1[self.position_idxs[0]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot1.get_xy())
            self.forbidden_positions.append(self.positions1[self.position_idxs[0]])
            self.robot1.set_xy(self.positions1[self.position_idxs[0]])
            self.position_idxs[0] += 1
        if (self.positions2[self.position_idxs[1]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot2.get_xy())
            self.forbidden_positions.append(self.positions2[self.position_idxs[1]])
            self.robot2.set_xy(self.positions2[self.position_idxs[1]])
            self.position_idxs[1] += 1
        if (self.positions3[self.position_idxs[2]] not in self.forbidden_positions):
            self.forbidden_positions.remove(self.robot3.get_xy())
            self.forbidden_positions.append(self.positions3[self.position_idxs[2]])
            self.robot3.set_xy(self.positions3[self.position_idxs[2]])
            self.position_idxs[2] += 1

        # self.robot2.set_xy(self.positions2[self.position_idxs[1]])
        # self.robot3.set_xy(self.positions3[self.position_idxs[2]])
        self.draw()
        


class GUI(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tab Example")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QFrame()
        central_widget.setStyleSheet(StyleSheet.CentralWidget.value)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.setStyleSheet(StyleSheet.Tab.value)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")
        self.tabs.addTab(self.tab3, "Tab 3")

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.snake = Snake(self, width=5, height=4, dpi=100)
        self.robot_sim = RobotSimulation(self, width=5, height=4, dpi=100)

        self.create_tab_content()
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def create_tab_content(self):
        sub_tab_widget = QTabWidget()
        sub_tab_widget.setTabPosition(QTabWidget.West)
        sub_tab_widget.setStyleSheet(StyleSheet.SubTab.value)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.robot_sim)
        self.robot_sim.start_moving()
        self.tab1.setLayout(layout1)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.snake)
        # self.snake.start_moving()
        self.tab2.setLayout(layout2)

        layout3 = QVBoxLayout()
        layout3.addWidget(self.canvas)
        self.tab3.setLayout(layout3)

def main():
    app = QApplication([])
    app.setStyleSheet(StyleSheet.App.value)
    window = GUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
