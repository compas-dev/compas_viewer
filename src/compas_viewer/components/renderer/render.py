# import time
# from typing import Dict
# from typing import List
# from typing import Literal
# from typing import Tuple
# from typing import TypedDict

# from compas.geometry import transform_points_numpy
# from OpenGL import GL
# from qtpy import QtCore
# from qtpy import QtWidgets
# from qtpy.QtGui import QKeyEvent
# from qtpy.QtGui import QMouseEvent

# from .camera import Camera
# from .grid import Grid
# from .objects import BufferObject
# from .objects import ViewerObject
# from .shader import Shader
# from .selector import Selector


# class RenderConfigData(TypedDict):
#     show_grid: bool
#     grid_size: Tuple[float, float, int, int]
#     view_mode: Literal["front", "right", "top", "perspective"]
#     render_mode: Literal["wireframe", "shaded", "ghosted", "lighted"]
#     background_color: Tuple[float, float, float, float]
#     selection_color: Tuple[float, float, float, float]


# class Render(QtWidgets.QOpenGLWidget):  # type: ignore
#     """
#     Render class for 3D rendering of COMPAS geometry.
#     We constantly use OpenGL version 2.1 and GLSL 120 with a Compatibility Profile at the moment.
#     The width and height are not in its configuration since they are set by the parent layout.

#     Parameters
#     ---------------
#     config : RenderConfigData
#         A TypedDict with the following keys:
#             show_grid: bool
#             view_mode: Literal["front", "right", "top", "perspective"]
#             render_mode: Literal["wireframe", "shaded", "ghosted", "lighted"]
#             background_color: Tuple[float, float, float, float]
#             selection_color: Tuple[float, float, float, float]
#     width: int
#         The width of the render.
#     height: int
#         The height of the render.

#     """

#     def __init__(self, config: RenderConfigData, width: int, height: int) -> None:
#         super().__init__()
#         self.config = config
#         self.width = width
#         self.height = height
#         self.background_color = self.config["background_color"]
#         self.view_mode = self.config["view_mode"]
#         self.selection_color = self.config["selection_color"]
#         self.show_grid = self.config["show_grid"]

#         self.camera = Camera(self)
#         self.grid = Grid(self.config["grid_size"])
#         self.selector = Selector(self)
#         self.objects: Dict[str, ViewerObject] = {}

#         self._frames = 0
#         self._now: float = time.time()

#         self.setFocusPolicy(QtCore.Qt.StrongFocus)  # type: ignore

#     # ==========================================================================
#     # gl
#     # ==========================================================================
#     def clearGL(self) -> None:
#         """Clear the view."""
#         GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

#     def initializeGL(self) -> None:
#         """Initialize the OpenGL canvas.

#         This implements the virtual funtion of the OpenGL widget.
#         See the PySide2 docs [1]_ for more info.
#         It sets the clear color of the view,
#         and enables culling, depth testing, blending, point smoothing, and line smoothing.

#         To extend the behaviour of this function,
#         you can implement :meth:`~compas_view2.views.View.init`.

#         References
#         ---------------
#         .. [1] https://doc.qt.io/qtforpython-5.12/PySide2/QtWidgets/QOpenGLWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QOpenGLWidget.initializeGL

#         """
#         GL.glClearColor(*self.background_color)
#         GL.glPolygonOffset(1.0, 1.0)
#         GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
#         GL.glEnable(GL.GL_CULL_FACE)
#         GL.glCullFace(GL.GL_BACK)
#         GL.glEnable(GL.GL_DEPTH_TEST)
#         GL.glDepthFunc(GL.GL_LESS)
#         GL.glEnable(GL.GL_BLEND)
#         GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
#         GL.glEnable(GL.GL_POINT_SMOOTH)
#         GL.glEnable(GL.GL_LINE_SMOOTH)
#         GL.glEnable(GL.GL_FRAMEBUFFER_SRGB)

#     def resizeGL(self, w, h) -> None:
#         """Resize the OpenGL canvas.

#         This implements the virtual funtion of the OpenGL widget.
#         See the PySide2 docs [1]_ for more info.

#         To extend the behaviour of this function,
#         you can implement :meth:`~compas_view2.views.View.resize`.

#         Parameters
#         ----------
#         w: float
#             The width of the canvas.
#         h: float
#             The height of the canvas.

#         References
#         ----------
#         .. [1] https://doc.qt.io/qtforpython-5.12/PySide2/QtWidgets/QOpenGLWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QOpenGLWidget.resizeGL

#         """
#         self.width = w
#         self.height = h
#         GL.glViewport(0, 0, w, h)

#     def paintGL(self) -> None:
#         """Paint the OpenGL canvas.

#         This implements the virtual funtion of the OpenGL widget.
#         See the PySide2 docs [1]_ for more info.

#         To extend the behaviour of this function,
#         you can implement :meth:`~compas_view2.views.View.paint`.

#         Notes
#         -----
#         This method also paints the instance map used by the selector to identify selected objects.
#         The instance map is immediately cleared again, after which the real scene objects are drawn.

#         References
#         ----------
#         .. [1] https://doc.qt.io/qtforpython-5.12/PySide2/QtWidgets/QOpenGLWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QOpenGLWidget.paintGL

#         """
#         self.clear()
#         self._frames += 1
#         if time.time() - self._now > 1:
#             self._now = time.time()
#             self.viewer.fps(self._frames)
#             self._frames = 0

#     # ==========================================================================
#     # event
#     # ==========================================================================

#     def mouseMoveEvent(self, event) -> Tuple[bool, QMouseEvent]:
#         """Callback for the mouse move event.

#         This method registers selections, if the left button is pressed,
#         and modifies the view (pan/rotate), if the right button is pressed.

#         Parameters
#         ----------
#         event : PySide2.QtGui.QMouseEvent
#             The Qt event.
#         """
#         return (not self.isActiveWindow() or not self.underMouse(), event)

#     def mousePressEvent(self, event) -> Tuple[bool, QMouseEvent]:
#         """Callback for the mouse press event.

#         Parameters
#         ----------
#         event : PySide2.QtGui.QMouseEvent
#             The Qt event.
#         """
#         return (not self.isActiveWindow() or not self.underMouse(), event)

#     def mouseReleaseEvent(self, event) -> Tuple[bool, QMouseEvent]:
#         """Callback for the release press event.

#         Parameters
#         ----------
#         event : PySide2.QtGui.QMouseEvent
#             The Qt event.
#         """
#         return (not self.isActiveWindow() or not self.underMouse(), event)

#     def wheelEvent(self, event) -> Tuple[bool, QMouseEvent]:
#         """Callback for the mouse wheel event.

#         Parameters
#         ----------
#         event : PySide2.QtGui.QMouseEvent
#             The Qt event.
#         """
#         return (not self.isActiveWindow() or not self.underMouse(), event)

#     def keyPressEvent(self, event) -> Tuple[bool, QKeyEvent]:
#         """Callback for the key press event.

#         Parameters
#         ----------
#         event : PySide2.QtGui.QMouseEvent
#             The Qt event.
#         """
#         return (True, event)

#     def keyReleaseEvent(self, event) -> Tuple[bool, QKeyEvent]:
#         """Callback for the key release event.

#         Parameters
#         ----------
#         event : PySide2.QtGui.QMouseEvent
#             The Qt event.
#         """
#         return (True, event)

#     # ==========================================================================
#     # view
#     # ==========================================================================
#     def init(self) -> None:
#         self.grid.init()

#         # init the buffers
#         for guid in self.objects:
#             obj = self.objects[guid]
#             obj.init()

#         projection = self.camera.projection(self.width, self.height)
#         viewworld = self.camera.viewworld()
#         transform = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]

#         self.shader_model = Shader(name="120/model")
#         self.shader_model.bind()
#         self.shader_model.uniform4x4("projection", projection)
#         self.shader_model.uniform4x4("viewworld", viewworld)
#         self.shader_model.uniform4x4("transform", transform)
#         self.shader_model.uniform1i("is_selected", 0)
#         self.shader_model.uniform1f("opacity", self.opacity)
#         self.shader_model.uniform3f("selection_color", self.selection_color)
#         self.shader_model.release()

#         self.shader_text = Shader(name="120/text")
#         self.shader_text.bind()
#         self.shader_text.uniform4x4("projection", projection)
#         self.shader_text.uniform4x4("viewworld", viewworld)
#         self.shader_text.uniform4x4("transform", transform)
#         self.shader_text.uniform1f("opacity", self.opacity)
#         self.shader_text.release()

#         self.shader_arrow = Shader(name="120/arrow")
#         self.shader_arrow.bind()
#         self.shader_arrow.uniform4x4("projection", projection)
#         self.shader_arrow.uniform4x4("viewworld", viewworld)
#         self.shader_arrow.uniform4x4("transform", transform)
#         self.shader_arrow.uniform1f("opacity", self.opacity)
#         self.shader_arrow.uniform1f("aspect", self.width / self.height)
#         self.shader_arrow.release()

#         self.shader_instance = Shader(name="120/instance")
#         self.shader_instance.bind()
#         self.shader_instance.uniform4x4("projection", projection)
#         self.shader_instance.uniform4x4("viewworld", viewworld)
#         self.shader_instance.uniform4x4("transform", transform)
#         self.shader_instance.release()

#         self.shader_grid = Shader(name="120/grid")
#         self.shader_grid.bind()
#         self.shader_grid.uniform4x4("projection", projection)
#         self.shader_grid.uniform4x4("viewworld", viewworld)
#         self.shader_grid.uniform4x4("transform", transform)
#         self.shader_grid.release()

#     def update_projection(self) -> None:
#         """
#         Update the projection matrix of the shaders.
#         """

#         projection = self.camera.projection(self.width, self.height)
#         self.shader_model.bind()
#         self.shader_model.uniform4x4("projection", projection)
#         self.shader_model.release()

#         self.shader_text.bind()
#         self.shader_text.uniform4x4("projection", projection)
#         self.shader_text.release()

#         self.shader_arrow.bind()
#         self.shader_arrow.uniform4x4("projection", projection)
#         self.shader_arrow.uniform1f("aspect", self.width / self.height)
#         self.shader_arrow.release()

#         self.shader_instance.bind()
#         self.shader_instance.uniform4x4("projection", projection)
#         self.shader_instance.release()

#         self.shader_grid.bind()
#         self.shader_grid.uniform4x4("projection", projection)
#         self.shader_grid.release()

#     resize = update_projection

#     def sort_objects_from_viewworld(self, viewworld) -> List[ViewerObject]:  # -> list[Any]:
#         """Sort transparent objects by the distances from their bounding box centers to camera location"""
#         opaque_objects: List[ViewerObject] = []
#         transparent_objects: List[ViewerObject] = []
#         centers: List[Tuple[float, float, float]] = []

#         for guid in self.objects:
#             obj = self.objects[guid]
#             if isinstance(obj, BufferObject):
#                 if obj.opacity * self.opacity < 1 and obj.bounding_box_center is not None:
#                     transparent_objects.append(obj)
#                     centers.append(transform_points_numpy([obj.bounding_box_center], obj.matrix)[0])
#                 else:
#                     opaque_objects.append(obj)
#         if transparent_objects:
#             centers = transform_points_numpy(centers, viewworld)
#             transparent_objects.sort(key=lambda obj: centers[transparent_objects.index(obj)][2])

#         return opaque_objects + transparent_objects
