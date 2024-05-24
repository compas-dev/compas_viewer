from PySide6.QtWidgets import QMainWindow


class MainWindow:
    def __init__(self, title):
        self.title = title
        self.widget = QMainWindow()
        self.widget.setWindowTitle(title)
