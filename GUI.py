from PyQt5.QtWidgets import ( 
    QMainWindow, 
    QTabWidget, 
    QWidget, 
    QVBoxLayout, 
    QFrame
)
from utils.StyleSheet import StyleSheet

from mpl_widgets.SingleBezierCurve import SingleBezierCurve
from mpl_widgets.PathCreationAlgorithm import PathCreationAlgorithm
        


class GUI(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MMRS Simulator")
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

        self.single_bc = SingleBezierCurve(self, width=5, height=4, dpi=100)
        self.path_creation_algorithm = PathCreationAlgorithm(self, width=5, height=4, dpi=100)

        self.create_tabs_content()
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def create_tabs_content(self):
        sub_tab_widget = QTabWidget()
        sub_tab_widget.setTabPosition(QTabWidget.West)
        sub_tab_widget.setStyleSheet(StyleSheet.SubTab.value)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.path_creation_algorithm)
        self.tab1.setLayout(layout1)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.single_bc)
        self.tab2.setLayout(layout2)

        # layout3 = QVBoxLayout()
        # layout3.addWidget(self.path_creation_algorithm)
        # self.tab3.setLayout(layout3)