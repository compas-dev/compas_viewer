import pathlib
import sys

from OpenGL import GL
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget

from compas_viewer.config import Config
from compas_viewer.scene.scene import ViewerScene


def new_file():
    print("new file...")


def test_action():
    print("test action...")


class MenuBar:
    def __init__(self, ui: "UI") -> None:
        self.ui = ui
        self.window = self.ui.window
        self.widget = self.window.menuBar()

        filemenu = self.widget.addMenu("File")
        filemenu.addAction("New File...", new_file)


class ToolBar:
    def __init__(self, ui: "UI") -> None:
        self.ui = ui
        self.window = self.ui.window
        self.widget = self.window.addToolBar("Tools")
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")

        icon = QtGui.QIcon(str(pathlib.Path(__file__).parent.parent / "src" / "compas_viewer" / "icons" / "zoom_selected.svg"))
        button = QtWidgets.QPushButton()
        button.setToolTip("Zoom")
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(12, 12))
        button.clicked.connect(test_action)

        self.widget.addWidget(button)


class OpenGLWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()

    def clear(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

    def initializeGL(self):
        GL.glClearColor(0.7, 0.7, 0.7, 1.0)
        GL.glPolygonOffset(1.0, 1.0)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_FRAMEBUFFER_SRGB)

    def resizeGL(self, w: int, h: int):
        GL.glViewport(0, 0, w, h)


class View3D:
    def __init__(self, viewport: "ViewPort") -> None:
        self.viewport = viewport
        self.viewmode = "perspective"
        self.renderer = OpenGLWidget()


class SceneTreeView:
    def __init__(self) -> None:
        self.widget = QtWidgets.QFrame()
        self.widget.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)


class ObjectListView:
    def __init__(self) -> None:
        self.widget = QtWidgets.QFrame()
        self.widget.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)


class DoubleEditWidget:
    def __init__(self, label, value, minval, maxval):
        self.widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QHBoxLayout()
        self.validator = QtGui.QDoubleValidator()
        self.validator.setRange(minval, maxval)
        self.label = QtWidgets.QLabel()
        self.label.setText(label)
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setText(str(value))
        self.line_edit.setValidator(self.validator)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)


class DoubleSpinnerWidget:
    def __init__(self, label, value, minval, maxval):
        self.widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QHBoxLayout()
        self.spinner = QtWidgets.QSpinBox()
        self.label = QtWidgets.QLabel()
        self.label.setText(label)
        self.spinner.setMinimum(minval)
        self.spinner.setMaximum(maxval)
        self.spinner.setValue(value)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinner)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)


class CameraTargetWidget:
    def __init__(self):
        self.widget = QtWidgets.QGroupBox()
        self.layout = QtWidgets.QVBoxLayout()
        self.x = DoubleEditWidget("X", 0, 0, 100000)
        self.y = DoubleEditWidget("Y", 0, 0, 100000)
        self.z = DoubleEditWidget("Z", 0, 0, 100000)
        self.layout.addWidget(self.x.widget)
        self.layout.addWidget(self.y.widget)
        self.layout.addWidget(self.z.widget)
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.widget.setTitle("Camera target")
        self.widget.setLayout(self.layout)


class CameraLocationWidget:
    def __init__(self):
        self.widget = QtWidgets.QGroupBox()
        self.layout = QtWidgets.QVBoxLayout()
        self.x = DoubleEditWidget("X", 0, 0, 100000)
        self.y = DoubleEditWidget("Y", 0, 0, 100000)
        self.z = DoubleEditWidget("Z", 0, 0, 100000)
        self.layout.addWidget(self.x.widget)
        self.layout.addWidget(self.y.widget)
        self.layout.addWidget(self.z.widget)
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.widget.setTitle("Camera location")
        self.widget.setLayout(self.layout)


class CameraSettings:
    def __init__(self) -> None:
        self.layout = QtWidgets.QVBoxLayout()
        self.widget = QtWidgets.QFrame()
        self.widget.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.widget.setLayout(self.layout)

        fov = DoubleSpinnerWidget("FOV", 50, 10, 80)
        near = DoubleSpinnerWidget("NEAR", 0.1, 0.001, 1000)
        far = DoubleSpinnerWidget("FAR", 1000, 1, 10000000)
        target = CameraTargetWidget()
        location = CameraLocationWidget()

        self.layout.addWidget(target.widget)
        self.layout.addWidget(location.widget)
        self.layout.addWidget(fov.widget)
        self.layout.addWidget(near.widget)
        self.layout.addWidget(far.widget)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.addStretch()


class SideBarRight:
    def __init__(self, viewport: "ViewPort") -> None:
        self.viewport = viewport
        self.scenetree = SceneTreeView()
        self.objectlist = ObjectListView()
        self.camerasettings = CameraSettings()

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.addWidget(self.scenetree.widget)
        self.splitter.addWidget(self.objectlist.widget)
        self.splitter.addWidget(self.camerasettings.widget)


class ViewPort:
    def __init__(self, ui: "UI"):
        self.ui = ui
        self.view3d = View3D(self)
        self.sidebar = SideBarRight(self)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.view3d.renderer)
        self.splitter.addWidget(self.sidebar.splitter)


class SatusBar:
    def __init__(self, ui: "UI") -> None:
        self.ui = ui
        self.window = self.ui.window
        self.widget = self.window.statusBar()
        self.label = QtWidgets.QLabel()
        self.widget.addWidget(self.label)
        self.set_status("Ready...")

    def set_status(self, status: str) -> None:
        self.label.setText(status)


class MainWindow(QMainWindow):
    def __init__(self, ui: "UI"):
        super().__init__()
        self.ui = ui
        layout = QtWidgets.QHBoxLayout()
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)


class UI:
    def __init__(self, viewer: "Viewer") -> None:
        self.viewer = viewer
        self.window = MainWindow(self)
        self.window.setWindowTitle(self.viewer.config.window.title)

        self.menubar = MenuBar(self)

        self.statusbar = SatusBar(self)
        self.statusbar.widget.setHidden(not self.viewer.config.ui.statusbar.show)

        self.toolbar = ToolBar(self)
        self.toolbar.widget.setHidden(not self.viewer.config.ui.toolbar.show)

        self.viewport = ViewPort(self)
        self.window.centralWidget().layout().addWidget(self.viewport.splitter)

        self.viewport.sidebar.splitter.setHidden(not self.viewer.config.ui.sidebar.show)

    def init(self):
        width = self.viewer.config.window.width
        height = self.viewer.config.window.height
        self.resize(width, height)

    def show(self):
        self.window.show()

    def resize(self, w: int, h: int) -> None:
        self.window.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.setGeometry(x, y, w, h)


class Viewer:
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.config = Config()
        self.ui = UI(self)
        self.scene = ViewerScene(self, name="ViewerScene", context="Viewer")
        self.is_started = False

    def init(self):
        self.ui.init()

    def show(self):
        self.ui.init()
        self.ui.show()
        self.is_started = True
        self.app.exec()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.show()
