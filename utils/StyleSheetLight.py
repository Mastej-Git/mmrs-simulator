from enum import Enum

class StyleSheetLight(Enum):

    QPushButton = """
        QPushButton {
            background-color: #e0e0e0;
            color: #00cccc;
            border: 1px solid #e0e0e0;
            height: 50px;
        }

        QPushButton:hover {
            background-color: #f5f5f5;
            border: 1px solid #00cccc;
        }
    """

    QRadioButton = """
        QRadioButton {
            color: #00cccc;
            padding: 5px;
            background-color: #ebebeb;
        }

        QRadioButton::indicator:checked {
            background-color: #00cccc;
            border: 2px solid #00cccc;
        }

        QRadioButton:hover {
            background-color: #f5f5f5;
            border: 1px solid #00cccc;
        }

        QRadioButton::indicator:hover {
            border: 2px solid #00cccc;
        }
    """

    QComboBox = """
        QComboBox {
            background-color: #e0e0e0;
            color: #00cccc;
            height: 40px;
            border: 1px solid #e0e0e0;
            padding: 5px;
            border-radius: 3px;
            combobox-popup: 0;
        }

        QComboBox:hover {
            background-color: #f5f5f5;
            border: 1px solid #00cccc;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #00cccc;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            background-color: #e0e0e0;
        }

        QComboBox::down-arrow {
            image: url(down-arrow.png);
            width: 10px;
            height: 10px;
        }

        QComboBox QAbstractItemView {
            background-color: #e0e0e0;
            color: #00cccc;
            selection-background-color: #f5f5f5;
            selection-color: #00cccc;
            border: 1px solid #00cccc;
        }
    """

    QLabel = """
        QLabel {
            color: #00cccc;
            padding: 5px;
            border-radius: 3px;
            height: 30px;
            background-color: #ebebeb;
        }
    """

    InfoLabel = """
        QLabel {
            color: #00cccc;
            padding: 5px;
            border-radius: 3px;
            height: 30px;
            background-color: #f5f5f5;
        }
    """

    Tab = """
        QTabWidget::pane {
            border: none;
        }

        QTabBar::tab {
            background: #f5f5f5;
            color: #555555;
            width: 260px;
            height: 40px;
        }

        QTabBar::tab:selected {
            background: #e0e0e0;
            color: #00cccc;
            font-weight: bold;
        }
    """

    SubTab = """
        QTabBar::tab {
            background: #f5f5f5;
            color: #555555;
            width: 50px;
            height: 140px;
        }

        QTabBar::tab:selected {
            background: #e0e0e0;
            color: #00cccc;
            font-weight: bold;
        }
    """

    App = """
        QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }

        QLabel {
            color: #333333;
        }
    """

    CentralWidget = """
        QFrame {
            border: 1px solid #f5f5f5;
            border-radius: 10px;
            background-color: #f5f5f5;
        }
    """

    QGroupBox = """
        QGroupBox {
            border: 1px solid #aaaaaa;
        }
    """

    StatusLabel = """
        QLabel {
            font-size: 14px;
            color: #666666;
            padding: 5px;
        }
    """

    QGroupBoxStatistics = """
        QGroupBox {
            font-size: 16px;
            font-weight: bold;
            color: #111111;
            border: 2px solid #bbbbbb;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 5px;
        }
    """

    TimeLabel = lambda large=False: f"""
        QLabel {{
            font-size: {"24px" if large else "14px"};
            font-weight: bold;
            color: #00FF00;
            padding: 10px;
        }}
    """
