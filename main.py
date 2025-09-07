from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QTabWidget, 
    QWidget, 
    QVBoxLayout, 
    QFrame
)
from StyleSheet import StyleSheet

from mpl_widgets.mpl_canvas import MplCanvas
from mpl_widgets.snake import Snake
from mpl_widgets.robot_sim import RobotSimulation
        


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
        # self.robot_sim.start_moving()
        self.tab1.setLayout(layout1)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.snake)
        # self.snake.start_moving()
        self.tab2.setLayout(layout2)

        layout3 = QVBoxLayout()
        layout3.addWidget(self.canvas)
        # self.canvas.start_moving()
        self.tab3.setLayout(layout3)

def main():
    app = QApplication([])
    app.setStyleSheet(StyleSheet.App.value)
    window = GUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
