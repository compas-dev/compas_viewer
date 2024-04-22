from typing import TYPE_CHECKING
from typing import Optional
from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QMainWindow

if TYPE_CHECKING:
    from .ui import UI

class MainWindow(QMainWindow):
    def __init__(self, ui: "UI"):
        super().__init__()
        self.ui = ui
        self.config = ui.viewer.config.window
        self.init_window()

    def init_window(self):
        self.set_window_title()
        self.set_window_central()

    def set_window_title(self, title: Optional[str] = None) -> None:
        if title is None:
            title = self.config.title
        self.setWindowTitle(title)
    
    def set_window_central(self) -> None:
        layout = QtWidgets.QHBoxLayout()
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
