from PySide6 import QtCore
from PySide6 import QtWidgets


class SideBarRight:
    def __init__(self, show: bool = True) -> None:
        self.show = show
        self.widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.widget.setHidden(not self.show)
