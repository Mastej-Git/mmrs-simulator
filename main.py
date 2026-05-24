from PyQt5.QtWidgets import (
    QApplication, 
)
from utils.StyleSheetDark import StyleSheetDark
from utils.StyleSheetLight import StyleSheetLight
from GUI import GUI
        

def main():
    app = QApplication([])
    app.setStyleSheet(StyleSheetLight.App.value)
    window = GUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
