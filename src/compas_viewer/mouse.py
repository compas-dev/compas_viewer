from PySide6.QtCore import QPoint


class Mouse:
    """
    Class representing mouse actions and movements.

    Attributes
    ----------
    pos : :QtCore:`QtCore.QPoint`
        The current position of the mouse on the screen.
    last_pos : :QtCore:`QtCore.QPoint`
        The last recorded position of the mouse on the screen.
    """

    def __init__(self):
        self.pos = QPoint()
        self.last_pos = QPoint()

    def dx(self):
        return self.pos.x() - self.last_pos.x()

    def dy(self):
        return self.pos.y() - self.last_pos.y()
