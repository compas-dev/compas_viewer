import time
from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import Tuple

from compas.geometry import transform_points_numpy
from OpenGL import GL
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy.QtGui import QKeyEvent
from qtpy.QtGui import QMouseEvent

if TYPE_CHECKING:
    # https://peps.python.org/pep-0484/#runtime-or-type-checking
    from compas_viewer import Viewer

from compas_viewer.configurations import RenderConfig

# from .camera import Camera

# from .grid import Grid
# from .objects import BufferObject
from .objects import ViewerObject

# from .selector import Selector
from .shaders import Shader


class Render(QtWidgets.QOpenGLWidget):  # type: ignore
    """
    Render class for 3D rendering of COMPAS geometry.
    We constantly use OpenGL version 2.1 and GLSL 120 with a Compatibility Profile at the moment.
    The width and height are not in its configuration since they are set by the parent layout.

    Parameters
    ---------------
    viewer : Viewer
        The viewer instance.
    config : RenderConfigData
        A TypedDict with defined keys and types.


    """

    def __init__(self, viewer: "Viewer", config: RenderConfig) -> None:
        super().__init__()

        self.config = config
        self.viewer = viewer

        self._viewmode = self.config.viewmode
        self._opacity = 1.0
        self._frames = 0
        self._now: float = time.time()
        self._shader_model = None

        # self.camera = Camera(self)
        # self.grid = Grid(self.config.grid_size)
        # self.selector = Selector(self)
        self.objects: Dict[str, ViewerObject] = {}

        self.setFocusPolicy(QtCore.Qt.StrongFocus)  # type: ignore

    @property
    def rendermode(self):
        return self._rendermode

    @rendermode.setter
    def rendermode(self, rendermode):
        self._rendermode = rendermode
        if rendermode == "ghosted":
            self._opacity = self.config.ghost_opacity
        else:
            self._opacity = 1.0
        if self._shader_model:
            self._shader_model.bind()
            self._shader_model.uniform1f("opacity", self._opacity)
            self._shader_model.release()
            self.update()

    @property
    def viewmode(self):
        return self._viewmode

    @viewmode.setter
    def viewmode(self, viewmode):
        self._viewmode = viewmode
        if self.shader_model:
            self.shader_model.bind()
            # self.shader_model.uniform4x4("projection", self.camera.projection(self.app.width, self.app.height))
            self.shader_model.release()
            self.update()

    @property
    def opacity(self):
        return self._opacity

    # ==========================================================================
    # gl
    # ==========================================================================
    def clear(self) -> None:
        """Clear the view."""
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

    def initializeGL(self) -> None:
        """Initialize the OpenGL canvas.

        Notes
        -----
        This implements the virtual function of the OpenGL widget.
        See the PySide2 docs [1]_ for more info.
        It sets the clear color of the view,
        and enables culling, depth testing, blending, point smoothing, and line smoothing.

        References
        ---------------
        .. [1] https://doc.qt.io/qtforpython-5.12/PySide2/QtWidgets/QOpenGLWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QOpenGLWidget.initializeGL
        """
        GL.glClearColor(*self.config.background_color)
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
        self.init()

    def resizeGL(self, w, h) -> None:
        """Resize the OpenGL canvas.

        Notes
        -----
        This implements the virtual function of the OpenGL widget.
        See the PySide2 docs [1]_ for more info.

        Parameters
        ----------
        w: float
            The width of the canvas.
        h: float
            The height of the canvas.

        References
        ----------
        .. [1] https://doc.qt.io/qtforpython-5.12/PySide2/QtWidgets/QOpenGLWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QOpenGLWidget.resizeGL

        """
        self.width = w
        self.height = h
        GL.glViewport(0, 0, w, h)

    def paintGL(self) -> None:
        """Paint the OpenGL canvas.

        Notes
        -----
        This implements the virtual function of the OpenGL widget.
        See the PySide2 docs [1]_ for more info.
        This method also paints the instance map used by the selector to identify selected objects.
        The instance map is immediately cleared again, after which the real scene objects are drawn.

        References
        ----------
        .. [1] https://doc.qt.io/qtforpython-5.12/PySide2/QtWidgets/QOpenGLWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QOpenGLWidget.paintGL

        """
        self.clear()
        self._frames += 1
        if time.time() - self._now > 1:
            self._now = time.time()
            self.viewer.fps(self._frames)
            self._frames = 0

    # ==========================================================================
    # event
    # ==========================================================================

    def mouseMoveEvent(self, event):
        """Callback for the mouse move event.

        This method registers selections, if the left button is pressed,
        and modifies the view (pan/rotate), if the right button is pressed.

        Parameters
        ----------
        event : PySide2.QtGui.QMouseEvent
            The Qt event.
        """
        pass

    def mousePressEvent(self, event):
        """Callback for the mouse press event.

        Parameters
        ----------
        event : PySide2.QtGui.QMouseEvent
            The Qt event.
        """
        pass

    def mouseReleaseEvent(self, event):
        """Callback for the release press event.

        Parameters
        ----------
        event : PySide2.QtGui.QMouseEvent
            The Qt event.
        """
        pass

    def wheelEvent(self, event):
        """Callback for the mouse wheel event.

        Parameters
        ----------
        event : PySide2.QtGui.QMouseEvent
            The Qt event.
        """
        pass

    def keyPressEvent(self, event):
        """Callback for the key press event.

        Parameters
        ----------
        event : PySide2.QtGui.QMouseEvent
            The Qt event.
        """
        pass

    def keyReleaseEvent(self, event):
        """Callback for the key release event.

        Parameters
        ----------
        event : PySide2.QtGui.QMouseEvent
            The Qt event.
        """
        pass

    # ==========================================================================
    # view
    # ==========================================================================
    def init(self) -> None:
        """Initialize the render."""

        # self.grid.init()
        projection = self.camera.projection(self.viewer.config.width, self.viewer.config.height)
        viewworld = self.camera.viewworld()

        # init the buffers
        for guid in self.objects:
            obj = self.objects[guid]
            obj.init()

        transform = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]

        self.shader_model = Shader(name="model")
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.uniform4x4("viewworld", viewworld)
        self.shader_model.uniform4x4("transform", transform)
        self.shader_model.uniform1i("is_selected", 0)
        self.shader_model.uniform1f("opacity", self.opacity)
        self.shader_model.uniform3f("selection_color", self.config.selection_color)
        self.shader_model.release()

        self.shader_text = Shader(name="text")
        self.shader_text.bind()
        self.shader_text.uniform4x4("projection", projection)
        self.shader_text.uniform4x4("viewworld", viewworld)
        self.shader_text.uniform4x4("transform", transform)
        self.shader_text.uniform1f("opacity", self.opacity)
        self.shader_text.release()

        self.shader_arrow = Shader(name="arrow")
        self.shader_arrow.bind()
        self.shader_arrow.uniform4x4("projection", projection)
        self.shader_arrow.uniform4x4("viewworld", viewworld)
        self.shader_arrow.uniform4x4("transform", transform)
        self.shader_arrow.uniform1f("opacity", self.opacity)
        self.shader_arrow.uniform1f("aspect", self.viewer.config.width / self.viewer.config.height)
        self.shader_arrow.release()

        self.shader_instance = Shader(name="instance")
        self.shader_instance.bind()
        self.shader_instance.uniform4x4("projection", projection)
        self.shader_instance.uniform4x4("viewworld", viewworld)
        self.shader_instance.uniform4x4("transform", transform)
        self.shader_instance.release()

        self.shader_grid = Shader(name="grid")
        self.shader_grid.bind()
        self.shader_grid.uniform4x4("projection", projection)
        self.shader_grid.uniform4x4("viewworld", viewworld)
        self.shader_grid.uniform4x4("transform", transform)
        self.shader_grid.release()
