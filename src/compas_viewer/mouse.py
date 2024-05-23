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
        self.window_start_point: QPoint = None
        self.window_end_point: QPoint = None
        self.is_tracing_a_window: bool = False

    def dx(self):
        return self.pos.x() - self.last_pos.x()

    def dy(self):
        return self.pos.y() - self.last_pos.y()
