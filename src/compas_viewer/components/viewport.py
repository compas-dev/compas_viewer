from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPaintEvent
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QStackedLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base
from compas_viewer.components.component import Component
from compas_viewer.renderer import Renderer

from .mainwindow import MainWindow
from .sidebar import SideBarRight


class _OverlayCanvas(QWidget, Base):
    """Paint transient 2D feedback above the OpenGL renderer."""

    def __init__(self, renderer: Renderer) -> None:
        super().__init__()
        self.renderer = renderer
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoFillBackground(False)

    def sync(self) -> None:
        """Synchronize visibility and schedule one overlay repaint."""
        visible = self.viewer._has_overlay_content()
        self.setVisible(visible)
        if visible:
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw overlays inside the ordinary QWidget paint lifecycle."""
        del event
        if not self.viewer._has_overlay_content():
            return
        painter = QPainter()
        if not painter.begin(self):
            return
        try:
            self.viewer._draw_overlays(self.renderer, painter)
        finally:
            painter.end()


class ViewPort(Component):
    """Combine the renderer and right sidebar in the main window.

    Parameters
    ----------
    window
        Main window that receives the viewport as its central widget.

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = QSplitter()
        self.renderer = Renderer()
        self._canvas = QWidget()
        self._canvas_layout = QStackedLayout(self._canvas)
        self._canvas_layout.setContentsMargins(0, 0, 0, 0)
        self._canvas_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self._canvas_layout.addWidget(self.renderer)
        self._overlay_canvas = _OverlayCanvas(self.renderer)
        self._canvas_layout.addWidget(self._overlay_canvas)
        self._canvas_layout.setCurrentWidget(self._overlay_canvas)
        self.renderer.frameSwapped.connect(self._overlay_canvas.sync)
        self._overlay_canvas.sync()
        self.widget.addWidget(self._canvas)
        self.sidebar = SideBarRight(self)
        self.widget.addWidget(self.sidebar.widget)
        sidebar_width = self.viewer.config.ui.sidebar.width
        self.widget.setSizes([self.viewer.config.window.width - sidebar_width, sidebar_width])
        self.widget.setStretchFactor(0, 1)
        self.widget.setStretchFactor(1, 0)
        window.widget.setCentralWidget(self.widget)

    def update_overlays(self) -> None:
        """Synchronize and repaint transient screen overlays."""
        self._overlay_canvas.sync()
