import os

from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog
)

class FileDialog(QWidget):

    def __init__(self):
        super().__init__()

    def get_file(self, dir_path: str) -> str:
        home_dir = os.environ.get('HOME')

        options = QFileDialog.Options()
        read_file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", os.getcwd() + dir_path,
            "All files (*);;YAML Files (*.yaml);;Map Files (*.map)",
            options=options
        )

        if read_file_name.endswith((".yaml", ".map")):
            return read_file_name

        return ""