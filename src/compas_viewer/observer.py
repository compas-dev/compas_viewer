from PySide6.QtCore import QTimer

from compas_viewer.base import Base


class Observer(Base):
    def __init__(self):
        self._observers = set(
            (
                self.viewer.renderer,
                self.viewer.ui.sidebar,
            )
        )

        self._time = None
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_observers)
        self.debounce_interval = 100

    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.add(observer)

    def remove_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def request_update(self):
        if not self.update_timer.isActive():
            self.update_timer.start(self.debounce_interval)

    def update_observers(self):
        for observer in self._observers:
            observer.update()
