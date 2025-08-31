from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QTabWidget, 
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QFrame
)
from StyleSheet import StyleSheet

import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches


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

        self.create_tab_content()
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def create_tab_content(self):
        sub_tab_widget = QTabWidget()
        sub_tab_widget.setTabPosition(QTabWidget.West)
        sub_tab_widget.setStyleSheet(StyleSheet.SubTab.value)

        layout1 = QVBoxLayout()
        # layout1.addWidget(QLabel("This is the content of Tab 1"))
        layout1.addWidget(self.canvas)
        self.tab1.setLayout(layout1)

        layout2 = QVBoxLayout()
        layout2.addWidget(QLabel("This is the content of Tab 2"))
        self.tab2.setLayout(layout2)

        layout3 = QVBoxLayout()
        layout3.addWidget(QLabel("This is the content of Tab 3"))
        self.tab3.setLayout(layout3)

def main():
    app = QApplication([])
    app.setStyleSheet(StyleSheet.App.value)
    window = GUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
