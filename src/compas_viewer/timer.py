from typing import Callable

from PySide6.QtCore import QTimer


class Timer:
    """
    A simple timer that calls a function at specified intervals.

    Parameters
    ----------
    interval : int
        Interval between subsequent calls to this function, in milliseconds.
    callback : Callable
        The function to call.
    singleshot : bool, optional
        If True, the timer is a singleshot timer.
        Default is False.

    """

    def __init__(self, interval: int, callback: Callable, singleshot: bool = False):
        self.timer = QTimer()
        self.timer.setInterval(interval)
        self.timer.timeout.connect(callback)
        self.timer.setSingleShot(singleshot)
        self.timer.start()

    def stop(self):
        self.timer.stop()
