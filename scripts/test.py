from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QWheelEvent
from PySide6.QtCore import Qt

class Renderer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setMinimumSize(400, 300)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(100, 100, 200))
        painter.drawRect(10, 10, 100, 100)  # Example drawing

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            print("Mouse Pressed at:", event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        print("Mouse Position:", event.pos())

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()  # Get the vertical wheel delta
        if delta > 0:
            print("Scrolled up")
        else:
            print("Scrolled down")
        event.accept()
        # Emit a signal here if needed, or call a method from a controller


from PySide6.QtCore import QObject, Signal, QPoint

class MainController(QObject):
    dataUpdated = Signal()
    zoomChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.data = None
        self.zoomLevel = 100

    def handle_user_interaction(self, position):
        print("Handling interaction at:", position)
        self.data = f"Interaction at {position}"
        self.dataUpdated.emit()

    def adjust_zoom(self, delta):
        self.zoomLevel += delta
        print(f"Zoom level changed to: {self.zoomLevel}")
        self.zoomChanged.emit(self.zoomLevel)
        
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PySide6 MVC Example')
        self.setGeometry(300, 300, 500, 400)
        self.controller = MainController()
        self.renderer = Renderer()
        
        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.renderer)
        
        # Connecting renderer mouse events to controller methods
        self.renderer.mousePressEvent = lambda event: self.controller.handle_user_interaction(event.pos())
        self.renderer.wheelEvent = lambda event: self.controller.adjust_zoom(10 if event.angleDelta().y() > 0 else -10)
        self.controller.dataUpdated.connect(self.on_data_updated)

    def on_data_updated(self):
        # Update the view when data changes
        print("Data Updated:", self.controller.data)

from PySide6.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    view = MainView()
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()