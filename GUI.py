from PyQt5.QtWidgets import ( 
    QMainWindow, 
    QTabWidget, 
    QWidget, 
    QVBoxLayout, 
    QFrame,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from utils.StyleSheet import StyleSheet

from mpl_widgets.SingleBezierCurve import SingleBezierCurve
from mpl_widgets.Visualizer import Visualizer
        


class GUI(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MMRS Simulator")
        self.setGeometry(100, 100, 1200, 800)
        # start application in full screen
        # note: this will make the main window fullscreen when constructed
        # call showFullScreen() here so the app opens fullscreen instead of fixed 800x600
        # self.showFullScreen()

        # timer used for periodic updates when "Run" is active
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(40)  # ~25 FPS, adjust as needed
        self._update_timer.timeout.connect(self._on_update_tick)

        central_widget = QFrame()
        central_widget.setStyleSheet(StyleSheet.CentralWidget.value)
        # ...existing code...
        # replace the single vertical layout with a horizontal layout:
        layout = QHBoxLayout(central_widget)

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
        self.visualizer = Visualizer(self, width=5, height=4, dpi=100)

        self.create_tabs_content()

        # add tabs to the left and control panel to the right
        layout.addWidget(self.tabs, 1)  # stretch factor 1 -> takes remaining space
        self.side_panel = self.create_control_panel()
        layout.addWidget(self.side_panel)
        self.setCentralWidget(central_widget)

    def create_control_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("controlPanel")
        panel.setFixedWidth(250)  # keep a constant width for the side panel
        # use existing central/app theme so the panel matches the rest of the UI
        # CentralWidget provides the same background as the main area
        panel.setStyleSheet(StyleSheet.CentralWidget.value)

        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setSpacing(8)

        title = QLabel("Controls")
        # reuse label style from StyleSheet for consistency
        title.setStyleSheet(StyleSheet.InfoLabel.value)

        vbox.addWidget(title)

        # make buttons attributes so handlers can change their states
        self.btn_run = QPushButton("Run")
        self.btn_pause = QPushButton("Pause")
        self.btn_reset = QPushButton("Reset")
        self.btn_export = QPushButton("Exit")
        # you can connect these buttons to your functions, e.g.:
        # btn_run.clicked.connect(self.on_run_clicked)

        for b in (self.btn_run, self.btn_pause, self.btn_reset, self.btn_export):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            # apply shared QPushButton styling from StyleSheet
            b.setStyleSheet(StyleSheet.QPushButton.value)
            vbox.addWidget(b)

        # connect signals
        self.btn_run.clicked.connect(self.on_run_clicked)
        self.btn_pause.clicked.connect(self.on_pause_clicked)
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        self.btn_export.clicked.connect(self.on_exit_clicked)

        # initial button state
        self.btn_pause.setEnabled(False)

        vbox.addStretch(1)  # push controls to the top

        return panel

    def create_tabs_content(self):
        sub_tab_widget = QTabWidget()
        sub_tab_widget.setTabPosition(QTabWidget.West)
        sub_tab_widget.setStyleSheet(StyleSheet.SubTab.value)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.visualizer)
        self.tab1.setLayout(layout1)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.single_bc)
        self.tab2.setLayout(layout2)

        # layout3 = QVBoxLayout()
        # layout3.addWidget(self.visualizer)
        # self.tab3.setLayout(layout3)

    # ----------------------
    # Button handlers below
    # ----------------------
    def on_run_clicked(self):
        self.btn_run.setEnabled(False)
        self.btn_pause.setEnabled(True)

        self.visualizer.timer.start(50)
        self.visualizer.simulation_f = True

    def on_pause_clicked(self):
        self.btn_run.setEnabled(True)
        self.btn_pause.setEnabled(False)

        self.visualizer.timer.stop()
        self.visualizer.simulation_f = False

    def on_reset_clicked(self):
        self.visualizer.reset_simulation()

    def on_exit_clicked(self):
        exit(0)

    def _on_update_tick(self):
        """Called by QTimer while running. Ask widgets to update/redraw."""
        for w in (self.path_creation_algorithm, self.single_bc):
            # try a few common refresh method names
            for method in ("update_plot", "redraw", "update", "repaint"):
                if hasattr(w, method):
                    try:
                        getattr(w, method)()
                    except Exception:
                        pass
                    break
