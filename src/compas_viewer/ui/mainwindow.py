from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget


class MainWindow:

    def __init__(self, title):
        self.title = title
        self.widget = QMainWindow()
        self.widget.setWindowTitle(title)
