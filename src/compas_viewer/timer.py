from collections.abc import Callable

from PySide6.QtCore import QTimer


class Timer:
    """Call a function at a fixed interval using a Qt timer.

    Parameters
    ----------
    interval
        Interval between subsequent calls to this function, in milliseconds.
    callback
        The function to call.
    singleshot
        If True, the timer is a singleshot timer.

    """

    def __init__(self, interval: int, callback: Callable[[], object], singleshot: bool = False) -> None:
        self.timer = QTimer()
        self.timer.setInterval(interval)
        self.timer.timeout.connect(callback)
        self.timer.setSingleShot(singleshot)
        self.timer.start()

    def stop(self) -> None:
        """Stop the timer."""
        self.timer.stop()
