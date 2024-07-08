import time
from functools import lru_cache
from typing import TYPE_CHECKING

from numpy import float32
from numpy import frombuffer
from numpy import identity
from numpy import uint8
from OpenGL import GL
from PySide6 import QtCore
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QGestureEvent

from compas.geometry import Frame
from compas.geometry import transform_points_numpy
from compas_viewer.scene import TagObject
from compas_viewer.scene.gridobject import GridObject
from compas_viewer.scene.vectorobject import VectorObject

from .camera import Camera
from .shaders import Shader

if TYPE_CHECKING:
    from compas_viewer import Viewer
    from compas_viewer.scene.gridobject import GridObject
    from compas_viewer.scene.meshobject import MeshObject


class Renderer(QOpenGLWidget):
    """
    Renderer class for 3D rendering of COMPAS geometry.
    We constantly use OpenGL version 2.1 and GLSL 120 with a Compatibility Profile at the moment.
    The width and height are not in its configuration since they are set by the parent layout.

    Parameters
    ----------
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer instance.
    config : :class:`compas_viewer.configurations.RendererConfig`
        The renderer configuration.
    """

    # The anti-aliasing factor for the drag selection.
    ANTI_ALIASING_FACTOR = 10

    # Enhance pixel  width for selection.
    PIXEL_SELECTION_INCREMENTAL = 2

    def __init__(self, viewer: "Viewer"):
        super().__init__()

        self.viewer = viewer

        self._view = self.viewer.config.renderer.view
        self._rendermode = self.viewer.config.renderer.rendermode
        self._opacity = self.viewer.config.renderer.ghostopacity if self.rendermode == "ghosted" else 1.0

        self._frames = 0
        self._now = time.time()

        self.grid = None

        self.shader_model: Shader = None
        self.shader_tag: Shader = None
        self.shader_arrow: Shader = None
        self.shader_instance: Shader = None
        self.shader_grid: Shader = None

        self.camera = Camera(
            self,
            fov=self.viewer.config.camera.fov,
            near=self.viewer.config.camera.near,
            far=self.viewer.config.camera.far,
            position=self.viewer.config.camera.position,
            target=self.viewer.config.camera.target,
            scale=self.viewer.config.camera.scale,
            zoomdelta=self.viewer.config.camera.zoomdelta,
            rotationdelta=self.viewer.config.camera.rotationdelta,
            pandelta=self.viewer.config.camera.pandelta,
        )

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.grabGesture(QtCore.Qt.GestureType.PinchGesture)

    @property
    def rendermode(self):
        """
        The renderer mode of the view.

        Returns
        -------
            The renderer mode of the view.
        """
        return self._rendermode

    @rendermode.setter
    def rendermode(self, rendermode):
        self._rendermode = rendermode
        self.viewer.config.renderer.rendermode = rendermode
        if rendermode == "ghosted":
            self._opacity = self.viewer.config.renderer.ghostopacity
        else:
            self._opacity = 1.0
        if self.shader_model:
            self.shader_model.bind()
            self.shader_model.uniform1f("opacity", self._opacity)
            self.shader_model.release()
            self.update()

    @property
    def view(self):
        """
        The view mode of the view.

        Returns
        -------
            The view mode of the view.
        """
        return self._view

    @view.setter
    def view(self, view):
        self._view = view
        self.camera.reset_position()
        if self.viewer.running:
            self.shader_model.bind()
            self.shader_model.uniform4x4("projection", self.camera.projection(self.width(), self.height()))
            self.shader_model.release()
            self.update_projection()
            self.update()

    @property
    def opacity(self) -> float:
        """
        The opacity of the view.

        Returns
        -------
        float
            The opacity of the view.
        """
        return self._opacity

    # ==========================================================================
    # GL
    # ==========================================================================

    def clear(self):
        """Clear the view.

        See Also
        --------
        :GL:`glClear`
        """
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

    def initializeGL(self):
        """
        Initialize the OpenGL canvas.

        Notes
        -----
        This implements the virtual function of the OpenGL widget.
        It sets the clear color of the view,
        and enables culling, depth testing, blending, point smoothing, and line smoothing.

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtOpenGL/QOpenGLWindow.html#PySide6.QtOpenGL.PySide6.QtOpenGL.QOpenGLWindow.initializeGL

        """
        GL.glClearColor(*self.viewer.config.renderer.backgroundcolor.rgba)
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

    def resizeGL(self, w: int, h: int):
        """
        Resize the OpenGL canvas.

        Parameters
        ----------
        w : int
            The width of the canvas.
        h : int
            The height of the canvas.

        Notes
        -----
        This implements the virtual function of the OpenGL widget.

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtOpenGL/QOpenGLWindow.html#PySide6.QtOpenGL.PySide6.QtOpenGL.QOpenGLWindow.resizeGL

        """
        GL.glViewport(0, 0, w, h)
        self.resize(w, h)

    def paintGL(self, is_instance: bool = False):
        """Paint the OpenGL canvas.

        Parameters
        ----------
        is_instance : bool, optional
            Whether the render is for instance map, by default False.

        Notes
        -----
        This implements the virtual function of the OpenGL widget.
        This method also paints the instance map used by the selector to identify selected objects.
        The instance map is immediately cleared again, after which the real scene objects are drawn.

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtOpenGL/QOpenGLWindow.html#PySide6.QtOpenGL.PySide6.QtOpenGL.QOpenGLWindow.paintGL

        """
        self.clear()
        if is_instance or self.rendermode == "instance":
            self.paint_instance()
        else:
            self.paint()

        self._frames += 1
        if time.time() - self._now > 1:
            self._now = time.time()
            self._frames = 0

    # ==========================================================================
    # Event
    # ==========================================================================

    def event(self, event: QtCore.QEvent):
        """
        Event handler for the renderer. Customised to capture multi-touch gestures.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtCore/QEvent`
            The Qt event.

        """
        if event.type() == QtCore.QEvent.Type.Gesture:
            return self.gestureEvent(event)
        return super().event(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Callback for the mouse move event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.

        """
        if self.isActiveWindow() and self.underMouse():
            self.viewer.eventmanager.delegate_mousemove(event)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Callback for the mouse press event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.

        """
        if self.isActiveWindow() and self.underMouse():
            self.viewer.eventmanager.delegate_mousepress(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Callback for the release press event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.

        """
        if self.isActiveWindow() and self.underMouse():
            self.viewer.eventmanager.delegate_mouserelease(event)

    def gestureEvent(self, event: QGestureEvent):
        """
        Callback for the gesture event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtCore/QEvent`
            The Qt event.

        """
        pinch = event.gesture(QtCore.Qt.GestureType.PinchGesture)
        if pinch:
            self.viewer.eventmanager.delegate_pinch(pinch)
            return True
        return False

    def wheelEvent(self, event: QWheelEvent):
        """
        Callback for the mouse wheel event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QWheelEvent`
            The Qt event.

        See Also
        --------
        :func:`compas_viewer.controller.Controller.wheel_action`

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.wheelEvent

        """
        if self.isActiveWindow() and self.underMouse():
            self.viewer.eventmanager.delegate_wheel(event)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Callback for the key press event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QKeyEvent`
            The Qt event.

        See Also
        --------
        :func:`compas_viewer.controller.Controller.key_press_action`

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.keyPressEvent

        """
        self.viewer.eventmanager.delegate_keypress(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        """
        Callback for the key release event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QKeyEvent`
            The Qt event.

        See Also
        --------
        :func:`compas_viewer.controller.Controller.key_release_action`

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.keyReleaseEvent

        """
        self.viewer.eventmanager.delegate_keyrelease(event)

    # ==========================================================================
    # view
    # ==========================================================================

    def init(self):
        """Initialize the renderer."""

        # Init the grid
        if self.viewer.config.renderer.show_grid:
            self.grid = GridObject(
                Frame.worldXY(),
                gridmode=self.viewer.config.renderer.gridmode,
                framesize=self.viewer.config.renderer.gridsize,
                show_framez=self.viewer.config.renderer.show_gridz,
                show=self.viewer.config.renderer.show_grid,
            )
            self.grid.init()

        # Init the buffers
        for obj in self.viewer.scene.objects:
            obj.init()

        projection = self.camera.projection(self.viewer.config.window.width, self.viewer.config.window.height)
        viewworld = self.camera.viewworld()
        transform = list(identity(4, dtype=float32))
        # create the program

        self.shader_model = Shader(name="model")
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.uniform4x4("viewworld", viewworld)
        self.shader_model.uniform4x4("transform", transform)
        self.shader_model.uniform1i("is_selected", 0)
        self.shader_model.uniform1f("opacity", self.opacity)
        self.shader_model.uniform3f("selection_color", self.viewer.config.renderer.selectioncolor.rgb)
        self.shader_model.release()

        self.shader_tag = Shader(name="tag")
        self.shader_tag.bind()
        self.shader_tag.uniform4x4("projection", projection)
        self.shader_tag.uniform4x4("viewworld", viewworld)
        self.shader_tag.uniform4x4("transform", transform)
        self.shader_tag.uniform1f("opacity", self.opacity)
        self.shader_tag.release()

        self.shader_arrow = Shader(name="arrow")
        self.shader_arrow.bind()
        self.shader_arrow.uniform4x4("projection", projection)
        self.shader_arrow.uniform4x4("viewworld", viewworld)
        self.shader_arrow.uniform4x4("transform", transform)
        self.shader_arrow.uniform1f("opacity", self.opacity)
        self.shader_arrow.uniform1f("aspect", self.width() / self.height())
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

    def update_projection(self, w=None, h=None):
        """
        Update the projection matrix.

        Parameters
        ----------
        w : int, optional
            The width of the renderer, by default None.
        h : int, optional
            The height of the renderer, by default None.
        """
        w = w or self.width()
        h = h or self.height()

        projection = self.camera.projection(w, h)
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.release()

        self.shader_tag.bind()
        self.shader_tag.uniform4x4("projection", projection)
        self.shader_tag.release()

        self.shader_arrow.bind()
        self.shader_arrow.uniform4x4("projection", projection)
        self.shader_arrow.uniform1f("aspect", w / h)
        self.shader_arrow.release()

        self.shader_instance.bind()
        self.shader_instance.uniform4x4("projection", projection)
        self.shader_instance.release()

        self.shader_grid.bind()
        self.shader_grid.uniform4x4("projection", projection)
        self.shader_grid.release()

    def resize(self, w: int, h: int):
        """
        Resize the renderer.

        Parameters
        ----------
        w : int
            The width of the renderer.
        h : int
            The height of the renderer.
        """
        self.update_projection(w, h)

    def sort_objects_from_viewworld(self, objects: list["MeshObject"], viewworld: list[list[float]]):
        """Sort objects by the distances from their bounding box centers to camera location

        Parameters
        ----------
        objects : list[:class:`compas_viewer.scene.meshobject.MeshObject`]
            The objects to be sorted.
        viewworld : list[list[float]]
            The viewworld matrix.

        Returns
        -------
        list
            A list of sorted objects.
        """
        opaque_objects = []
        transparent_objects = []
        centers = []

        for obj in objects:
            if obj.opacity * self.opacity < 1 and obj.bounding_box_center is not None:
                transparent_objects.append(obj)
                centers.append(transform_points_numpy([obj.bounding_box_center], obj.worldtransformation)[0])
            else:
                opaque_objects.append(obj)
        if transparent_objects:
            centers = transform_points_numpy(centers, viewworld)
            transparent_objects = sorted(zip(transparent_objects, centers), key=lambda pair: pair[1][2])
            transparent_objects, _ = zip(*transparent_objects)
        return opaque_objects + list(transparent_objects)

    @lru_cache(maxsize=3)
    def sort_objects_from_category(self, objs: tuple["MeshObject"]) -> tuple[list["TagObject"], list["VectorObject"], list["MeshObject"]]:
        """Sort objects by their categories

        Returns
        -------
        tuple(list[:class:`compas_viewer.scene.tagobject.TagObject`],
        list[:class:`compas_viewer.scene.vectorobject.VectorObject`],
        list[:class:`compas_viewer.scene.sceneobject.MeshObject`])
            A tuple of sorted objects.

        Notes
        -----
        This function is cached to improve the performance.

        References
        ----------
        * https://docs.python.org/3/library/functools.html#functools.lru_cache
        * https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)
        """
        tag_objs = []
        vector_objs = []
        mesh_objs = []

        def sort(obj):
            if isinstance(obj, TagObject):
                tag_objs.append(obj)
            elif isinstance(obj, VectorObject):
                vector_objs.append(obj)
            else:
                mesh_objs.append(obj)

        for obj in objs:
            sort(obj)

        return tag_objs, vector_objs, mesh_objs

    def paint(self):
        """
        Paint all the items in the render, which only be called by the paintGL function
        and determines the performance of the renders
        This function introduces decision tree for different render modes and settings.
        It is only  called by the :class:`compas_viewer.components.render.Render.paintGL` function.

        See Also
        --------
        :func:`compas_viewer.components.render.Render.paintGL`
        :func:`compas_viewer.components.render.Render.paint_instance`
        """

        #  Matrix update
        viewworld = self.camera.viewworld()
        self.update_projection()
        # Object categorization
        tag_objs, vector_objs, mesh_objs = self.sort_objects_from_category(self.viewer.scene.visiable_objects)

        # Draw model objects in the scene
        self.shader_model.bind()
        self.shader_model.uniform4x4("viewworld", viewworld)
        if self.grid is not None:
            self.grid.draw(self.shader_model)
        for obj in self.sort_objects_from_viewworld(mesh_objs, viewworld):
            obj.draw(self.shader_model, self.rendermode == "wireframe", self.rendermode == "lighted")
        self.shader_model.release()

        # Draw vector arrows
        self.shader_arrow.bind()
        self.shader_arrow.uniform4x4("viewworld", viewworld)
        for obj in vector_objs:
            obj.draw(self.shader_arrow)
        self.shader_arrow.release()

        # Draw text tag sprites
        self.shader_tag.bind()
        self.shader_tag.uniform4x4("viewworld", viewworld)
        for obj in tag_objs:
            obj.draw(self.shader_tag, self.camera.position)
        self.shader_tag.release()

        # draw 2D box for multi-selection
        if self.viewer.mouse.is_tracing_a_window:
            self.shader_model.draw_2d_box(
                (
                    self.viewer.mouse.window_start_point.x(),
                    self.viewer.mouse.window_start_point.y(),
                    self.viewer.mouse.last_pos.x(),
                    self.viewer.mouse.last_pos.y(),
                ),
                self.width(),
                self.height(),
            )

    def paint_instance(self):
        """
        Independent drawing function for the  instance map,
        which is only called by the :class:`compas_viewer.components.render.Render.paintGL` function.

        See Also
        --------
        :func:`compas_viewer.components.render.Render.paintGL`
        :func:`compas_viewer.components.render.Render.paint`

        """

        #  Matrix update
        viewworld = self.camera.viewworld()
        self.update_projection()
        # Object categorization
        _, _, mesh_objs = self.sort_objects_from_category(tuple(self.viewer.scene.objects))
        # Draw instance maps
        GL.glDisable(GL.GL_POINT_SMOOTH)
        GL.glDisable(GL.GL_LINE_SMOOTH)

        self.shader_instance.bind()
        self.shader_instance.uniform4x4("viewworld", viewworld)
        for obj in mesh_objs:
            obj.draw_instance(self.shader_instance, self.rendermode == "wireframe")
        self.shader_instance.release()

        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_LINE_SMOOTH)

    def read_instance_color(self, box: tuple[int, int, int, int]):
        """
        Paint the instance map quickly, and then read the color of the specified area.

        Parameters
        ----------
        box : tuple[int, int, int, int]
            The box area [x1, y1, x2, y2] to be read. x1=x2 and y1=y2 means a single point.

        Notes
        -----
        The instance map is used by the selector to identify selected objects.
        The mechanism of a :class:`compas_viewer.components.renderer.selector.Selector`
        is picking the color from instance map and then find the corresponding object.
        Anti aliasing, which is always force opened in many machines,  can cause color picking inaccuracy.

        The instance buffer created by the GL is based on the "device-independent pixels",
        while "physical pixels" is the common unit. The method :func:`PySide6.QtGui.QPaintDevice.devicePixelRatio()`
        plays a role in the conversion between the two units, which is different on different devices.
        For example, Mac Retina display has a devicePixelRatio of 2.0.
        This method contains an uniform-sampling-similar math operation,
        which is not absolutely accurate but enough for the selection.

        See Also
        --------
        :func:`compas_viewer.components.renderer.selector.Selector.ANTI_ALIASING_FACTOR`
        :attr:`compas_viewer.components.renderer.rendermode`

        References
        ----------
        * https://doc.qt.io/qt-6/qscreen.html#devicePixelRatio-prop
        * https://registry.khronos.org/OpenGL-Refpages/gl4/html/glReadPixels.xhtml
        * https://doc.qt.io/qt-6/qopenglwidget.html#makeCurrent
        """

        # Get the rectangle area.
        x1, y1, x2, y2 = box
        x, y = min(x1, x2), self.height() - max(y1, y2)
        width = max(self.PIXEL_SELECTION_INCREMENTAL, abs(x1 - x2))
        height = max(self.PIXEL_SELECTION_INCREMENTAL, abs(y1 - y2))
        r = self.viewer.renderer.devicePixelRatio()

        pixels_x = width * r
        pixels_y = height * r
        step_x = round(pixels_x / 1000) + 1
        step_y = round(pixels_y / 1000) + 1

        # Repaint the canvas with instance color.
        self.viewer.renderer.makeCurrent()
        self.viewer.renderer.paintGL(is_instance=True)

        # Adjust width and height based on the step
        width_adjusted = (width // step_x) * step_x
        height_adjusted = (height // step_y) * step_y

        # Read the pixel data with downsampling
        instance_buffer = GL.glReadPixels(int(x * r), int(y * r), int(width_adjusted * r), int(height_adjusted * r), GL.GL_RGB, GL.GL_UNSIGNED_BYTE)
        instance_map = frombuffer(instance_buffer, dtype=uint8).reshape(int(height_adjusted * r), int(width_adjusted * r), 3)

        # Downsample the data
        instance_map = instance_map[::step_y, ::step_x, :].reshape(-1, 3)
        return instance_map
