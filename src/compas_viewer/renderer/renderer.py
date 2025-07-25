import time
from typing import TYPE_CHECKING

import numpy as np
from numpy import float32
from numpy import identity
from OpenGL import GL
from PySide6 import QtCore
from PySide6.QtCore import QTimer
from PySide6.QtGui import QDragEnterEvent
from PySide6.QtGui import QDragMoveEvent
from PySide6.QtGui import QDropEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtGui import QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QGestureEvent

from compas.geometry import Frame
from compas.geometry import transform_points_numpy
from compas.scene import Group
from compas_viewer.base import Base
from compas_viewer.gl import OffscreenBufferContext
from compas_viewer.scene import TagObject
from compas_viewer.scene.buffermanager import BufferManager
from compas_viewer.scene.gridobject import GridObject

from .camera import Camera
from .shaders import Shader

if TYPE_CHECKING:
    from compas_viewer.scene.gridobject import GridObject
    from compas_viewer.scene.meshobject import MeshObject


class Renderer(QOpenGLWidget, Base):
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

    def __init__(self):
        format = QSurfaceFormat()
        format.setVersion(3, 3)
        format.setProfile(QSurfaceFormat.CoreProfile)
        format.setSamples(4)  # Enable 4x MSAA (optional, can be set to 8, etc.)
        QSurfaceFormat.setDefaultFormat(format)

        super().__init__()

        self._view = self.viewer.config.renderer.view
        self._rendermode = self.viewer.config.renderer.rendermode
        self._opacity = self.viewer.config.renderer.ghostopacity if self.rendermode == "ghosted" else 1.0

        self._frames = 0
        self._now = time.time()

        self.grid = None

        self.shader_model: Shader = None
        self.shader_lines: Shader = None
        self._shader_tag: Shader = None
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
        self.setAcceptDrops(True)

        self.buffer_manager = BufferManager()

        self.set_idle_refresh()

    def set_idle_refresh(self):
        """Set a low idle refresh rate of 10 FPS. Useful for GPU buffer updates delay."""
        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(100)
        self._idle_timer.timeout.connect(self.update)
        self._idle_timer.start()

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
            self.shader_lines.bind()
            self.shader_lines.uniform1f("opacity", self._opacity)
            self.shader_lines.release()
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

    @property
    def shader_tag(self) -> Shader:
        """Lazy initialization of tag shader.

        Returns
        -------
        Shader
            The tag shader, initialized on first access.
        """
        if self._shader_tag is None:
            projection = self.camera.projection(self.width(), self.height())
            viewworld = self.camera.viewworld()
            transform = list(identity(4, dtype=float32))

            self._shader_tag = Shader(name="tag")
            self._shader_tag.bind()
            self._shader_tag.uniform4x4("projection", projection)
            self._shader_tag.uniform4x4("viewworld", viewworld)
            self._shader_tag.uniform4x4("transform", transform)
            self._shader_tag.uniform1f("opacity", self.opacity)
            self._shader_tag.release()
        return self._shader_tag

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
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_MULTISAMPLE)
        GL.glEnable(GL.GL_FRAMEBUFFER_SRGB)
        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
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
        """Paint the OpenGL canvas."""
        self.clear()

        if is_instance or self.rendermode == "instance":
            GL.glViewport(0, 0, self.width(), self.height())  # Use unscaled viewport for FBO
            self.paint(is_instance=True)
        else:
            r = self.devicePixelRatio()
            GL.glViewport(0, 0, int(self.width() * r), int(self.height() * r))  # Normal scaled viewport
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

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Callback for the drag enter event to handle file drops.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QDragEnterEvent`
            The Qt drag enter event.
        """
        if event.mimeData().hasUrls():
            # Check if any of the URLs are JSON files
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(".json"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """
        Callback for the drag move event to handle file drops.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QDragMoveEvent`
            The Qt drag move event.
        """
        if event.mimeData().hasUrls():
            # Check if any of the URLs are JSON files
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(".json"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """
        Callback for the drop event to handle loading scene files.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QDropEvent`
            The Qt drop event.
        """
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(".json"):
                    filepath = url.toLocalFile()
                    # Import here to avoid circular imports
                    from compas_viewer.commands import load_from_file

                    success = load_from_file(self.viewer, filepath)
                    if success:
                        print(f"Successfully loaded scene from: {filepath}")
                        event.acceptProposedAction()
                        return
            print("No valid scene JSON files found in the dropped files.")
        event.ignore()

    # ==========================================================================
    # view
    # ==========================================================================

    def init(self):
        """Initialize the renderer."""
        # Create and bind a VAO (required in core-profile OpenGL).
        self._vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._vao)

        self.buffer_manager.clear()

        # Init the grid
        self.grid = GridObject(
            Frame.worldXY(),
            gridmode=self.viewer.config.renderer.gridmode,
            framesize=self.viewer.config.renderer.gridsize,
            show_framez=self.viewer.config.renderer.show_gridz,
            show=self.viewer.config.renderer.show_grid,
        )
        self.grid.init()

        for obj in self.viewer.scene.objects:
            if not isinstance(obj, Group):
                obj.init()

        for obj in self.viewer.scene.objects:
            if not isinstance(obj, TagObject):
                self.buffer_manager.add_object(obj)

        self.buffer_manager.create_buffers()

        # Unbind VAO when setup is complete.
        GL.glBindVertexArray(0)

        projection = self.camera.projection(self.viewer.config.window.width, self.viewer.config.window.height)
        viewworld = self.camera.viewworld()

        # create the program
        self.shader_model = Shader(name="model")
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.uniform4x4("viewworld", viewworld)
        self.shader_model.uniform1f("opacity", self.opacity)
        self.shader_model.uniform3f("selection_color", self.viewer.config.renderer.selectioncolor.rgb)
        self.shader_model.uniformBuffer("transformBuffer", self.buffer_manager.transform_texture, unit=0)
        self.shader_model.uniformBuffer("settingsBuffer", self.buffer_manager.settings_texture, unit=1)
        self.shader_model.release()

        self.shader_lines = Shader(name="modellines")
        self.shader_lines.bind()
        self.shader_lines.uniform4x4("projection", projection)
        self.shader_lines.uniform4x4("viewworld", viewworld)
        self.shader_lines.uniform1f("opacity", self.opacity)
        self.shader_lines.uniform3f("selection_color", self.viewer.config.renderer.selectioncolor.rgb)
        self.shader_lines.uniformBuffer("transformBuffer", self.buffer_manager.transform_texture, unit=0)
        self.shader_lines.uniformBuffer("settingsBuffer", self.buffer_manager.settings_texture, unit=1)
        self.shader_lines.release()

    def rebuild_buffers(self):
        """Rebuild the buffers."""
        GL.glBindVertexArray(self._vao)
        self.buffer_manager.clear()

        # Ensure all objects are initialized before adding to buffer
        for obj in self.viewer.scene.objects:
            if not isinstance(obj, (Group, TagObject)) and not obj._inited:
                obj.init()

        for obj in self.viewer.scene.objects:
            if not isinstance(obj, (Group, TagObject)):
                self.buffer_manager.add_object(obj)
        self.buffer_manager.create_buffers()
        GL.glBindVertexArray(0)

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

        self.shader_lines.bind()
        self.shader_lines.uniform4x4("projection", projection)
        self.shader_lines.release()

        self.shader_tag.bind()
        self.shader_tag.uniform4x4("projection", projection)
        self.shader_tag.release()

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

    def paint(self, is_instance: bool = False):
        """Paint all the items in the render"""

        # Bind the same VAO created in init()
        GL.glBindVertexArray(self._vao)

        viewworld = self.camera.viewworld()
        self.update_projection()

        # Update object settings (visibility, selection, etc.)
        self.buffer_manager.update_settings()

        # Update uniforms for both shaders
        for shader in [self.shader_model, self.shader_lines]:
            shader.bind()
            shader.uniform1f("opacity", self.opacity)
            shader.uniformBuffer("transformBuffer", self.buffer_manager.transform_texture, unit=0)
            shader.uniformBuffer("settingsBuffer", self.buffer_manager.settings_texture, unit=1)
            shader.uniform4x4("viewworld", viewworld)
            shader.uniform1i("is_instance", is_instance)
            shader.release()

        # Update viewport uniform for line shader
        self.shader_lines.bind()
        self.shader_lines.uniform2f("viewport", (self.width(), self.height()))
        self.shader_lines.release()

        # Draw the grid (skip during instance rendering since grid doesn't have instance colors)
        if self.viewer.config.renderer.show_grid and not is_instance:
            self.shader_model.bind()
            self.grid.draw(self.shader_model)
            self.shader_model.release()

        # Draw all the objects in the buffer manager
        self.buffer_manager.draw(
            self.shader_model,
            self.shader_lines,
            self.rendermode,
            is_instance=is_instance,
        )

        # Draw text tag sprites if there are any
        tag_objs = [obj for obj in self.viewer.scene.objects if isinstance(obj, TagObject)]
        if tag_objs:
            # release the model shader and bind the tag shader
            self.shader_tag.bind()
            self.shader_tag.uniform4x4("viewworld", viewworld)
            for obj in tag_objs:
                obj.draw(self.shader_tag, self.camera.position, self.width(), self.height())
            self.shader_tag.release()

        # draw 2D box for multi-selection
        if self.viewer.mouse.is_tracing_a_window:
            # Ensure the model shader is bound before drawing
            self.shader_model.bind()

            # Draw the selection box
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
            self.shader_model.release()

        # Unbind once we're done
        GL.glBindVertexArray(0)

    def read_instance_color(self, box: tuple[int, int, int, int]):
        """Read instance colors from the specified screen region.

        Parameters
        ----------
        box : tuple[int, int, int, int]
            Screen coordinates (x1, y1, x2, y2) defining the selection area.

        Returns
        -------
        numpy.ndarray
            Array of RGB color values for each pixel in the selection area.
        """
        # Calculate selection area
        x1, y1, x2, y2 = box
        x, y = min(x1, x2), self.height() - max(y1, y2)
        width = max(self.PIXEL_SELECTION_INCREMENTAL, abs(x1 - x2))
        height = max(self.PIXEL_SELECTION_INCREMENTAL, abs(y1 - y2))

        # Render to offscreen buffer and read pixels
        with OffscreenBufferContext(self.width(), self.height()) as fbo_context:
            self._render_instance_map()
            pixels = self._read_pixels(x, y, width, height)

            # Debug output if enabled
            if self.viewer.config.renderer.debug_instance:
                self._save_debug_images(box, x, y, width, height, fbo_context.viewport)

        return pixels.reshape(-1, 3)

    def _render_instance_map(self):
        """Render the scene in instance color mode."""
        # Set up rendering state for instance mode
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Temporarily disable blending for clean instance colors
        was_blend_enabled = GL.glIsEnabled(GL.GL_BLEND)
        GL.glDisable(GL.GL_BLEND)

        try:
            self.paintGL(is_instance=True)
            GL.glFlush()
            GL.glFinish()
        finally:
            # Restore blending state
            if was_blend_enabled:
                GL.glEnable(GL.GL_BLEND)

    def _read_pixels(self, x: int, y: int, width: int, height: int):
        """Read pixel data from the current framebuffer."""
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        buffer = GL.glReadPixels(x, y, width, height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE)
        return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 3)

    def _save_debug_images(self, box: tuple[int, int, int, int], x: int, y: int, width: int, height: int, viewport: tuple):
        """Save debug images when debugging is enabled."""

        from PIL import Image
        from PIL import ImageDraw

        x1, y1, x2, y2 = box

        # Read and save full frame
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        full_buffer = GL.glReadPixels(0, 0, self.width(), self.height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
        full_map = np.frombuffer(full_buffer, dtype=np.uint8).reshape(self.height(), self.width(), 4)
        full_image = Image.fromarray(full_map).transpose(Image.FLIP_TOP_BOTTOM)
        full_image.save("instance_debug_full.png")

        # Create version with selection box highlighted
        full_with_box = full_image.copy()
        draw = ImageDraw.Draw(full_with_box)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        full_with_box.save("instance_debug_full_with_box.png")

        # Save selection area
        box_pixels = self._read_pixels(x, y, width, height)
        box_image = Image.fromarray(box_pixels).transpose(Image.FLIP_TOP_BOTTOM)
        box_image.save("instance_debug_box.png")

        # Print debug info
        print("Saved debug images:")
        print("- Full frame: instance_debug_full.png")
        print("- Full frame with box: instance_debug_full_with_box.png")
        print("- Box area: instance_debug_box.png")
        print(f"Box coordinates: x={x}, y={y}, width={width}, height={height}")
        print(f"Original box: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        print(f"Window size: {self.width()}x{self.height()}")
        print(f"Viewport: {viewport}")
