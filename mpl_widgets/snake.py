from PyQt5.QtCore import QTimer, Qt

import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

import random



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
        if event.key() == Qt.Key_Space:
            self.timer.start(50)

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
