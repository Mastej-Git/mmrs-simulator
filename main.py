from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QFrame

class GUI(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tab Example")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QFrame()
        central_widget.setStyleSheet("""
            QFrame {
                border: 1px solid #2e2e2e;
                border-radius: 10px;
                background-color: #2e2e2e;
            }
        """)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: none; 
            }
            QTabBar::tab {
                background: #2e2e2e; 
                color: #b1b1b1; 
                width: 260px; 
                height: 40px;
            }
            QTabBar::tab:selected { 
                background: #404040; 
                color: #00ffff; 
                font-weight: bold;
            }
        """)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")
        self.tabs.addTab(self.tab3, "Tab 3")

        self.create_tab_content()
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def create_tab_content(self):
        sub_tab_widget = QTabWidget()
        sub_tab_widget.setTabPosition(QTabWidget.West)
        sub_tab_widget.setStyleSheet("""
            QTabBar::tab {
                background: #2e2e2e;
                color: #b1b1b1;
                width: 50px;
                height: 120px;
            }
            QTabBar::tab:selected {
                background: #404040;
                color: #00ffff;
                font-weight: bold;
            }
        """)

        layout1 = QVBoxLayout()
        layout1.addWidget(QLabel("This is the content of Tab 1"))
        self.tab1.setLayout(layout1)

        layout2 = QVBoxLayout()
        layout2.addWidget(QLabel("This is the content of Tab 2"))
        self.tab2.setLayout(layout2)

        layout3 = QVBoxLayout()
        layout3.addWidget(QLabel("This is the content of Tab 3"))
        self.tab3.setLayout(layout3)

def main():
    app = QApplication([])
    app.setStyleSheet("""
        QWidget {
            background-color: #2e2e2e;
            color: #b1b1b1;
        }
        QLabel {
            color: #b1b1b1;
        }
    """)
    window = GUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
