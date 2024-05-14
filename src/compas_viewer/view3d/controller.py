from PySide6.QtCore import QObject, Qt, Signal
from compas_viewer.base import Base

class View3dSignals(QObject):
    rotate = Signal(float)
    zoom = Signal(float)

class View3dController(QObject, Base):
    def __init__(self, view3d):
        super().__init__()
        self.view = view3d
        self.signals = View3dSignals()

        # Connect signals to view slots
        self.signals.rotate.connect(self.view.rotate)
        self.signals.zoom.connect(self.view.zoom)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.signals.rotate.emit(5)  # Rotate by 5 degrees

    def wheelEvent(self, event):
        zoom_factor = event.angleDelta().y() / 1200  # Adjust zoom factor based on wheel movement
        self.signals.zoom.emit(zoom_factor)
