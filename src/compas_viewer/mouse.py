from PySide6.QtCore import QPoint


class Mouse:
    """Track current, previous, and window-selection mouse positions."""

    DRAG_THRESHOLD = 3

    def __init__(self) -> None:
        self.pos = QPoint()
        self.last_pos = QPoint()
        self.press_pos: QPoint | None = None
        self.window_start_point: QPoint | None = None
        self.window_end_point: QPoint | None = None
        self.is_tracing_a_window = False

    def begin(self, position: QPoint) -> None:
        """Start tracking a pointer gesture.

        Parameters
        ----------
        position
            Pointer position at button press.

        """
        self.pos = QPoint(position)
        self.last_pos = QPoint(position)
        self.press_pos = QPoint(position)

    def end(self, position: QPoint) -> None:
        """Finish tracking a pointer gesture.

        Parameters
        ----------
        position
            Pointer position at button release.

        """
        self.pos = QPoint(position)
        self.last_pos = QPoint(position)
        self.press_pos = None

    def has_dragged(self) -> bool:
        """Return whether pointer movement has crossed the drag threshold."""
        if self.press_pos is None:
            return False
        dx = self.pos.x() - self.press_pos.x()
        dy = self.pos.y() - self.press_pos.y()
        return dx * dx + dy * dy >= self.DRAG_THRESHOLD**2

    def dx(self) -> int:
        """Return the horizontal displacement since the previous event.

        Returns
        -------
        int
            Horizontal displacement in pixels.

        """
        return self.pos.x() - self.last_pos.x()

    def dy(self) -> int:
        """Return the vertical displacement since the previous event.

        Returns
        -------
        int
            Vertical displacement in pixels.

        """
        return self.pos.y() - self.last_pos.y()
