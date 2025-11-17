from PyQt5.QtWidgets import (
    QApplication, 
)
from StyleSheet import StyleSheet
from GUI import GUI
        

def main():
    app = QApplication([])
    app.setStyleSheet(StyleSheet.App.value)
    window = GUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
