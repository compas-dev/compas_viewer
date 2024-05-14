import time
from numpy import float32
from numpy import identity

from OpenGL import GL
from PySide6 import QtCore
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from compas.colors import Color
from compas.geometry import transform_points_numpy
from compas_viewer.base import Base
from compas_viewer.components.renderer.shaders import Shader
from compas_viewer.view3d.controller import View3dController
from compas_viewer.view3d.camera import Camera
from compas_viewer.scene.meshobject import MeshObject



class OpenGLWidget(QOpenGLWidget, Base):
    def __init__(self) -> None:
        super().__init__()

        self.rotation_angle = 0
        self.scale = 1.0
        
        self._frames = 0
        self._now = time.time()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.grabGesture(QtCore.Qt.PinchGesture)
        self.camera = Camera()
        # self.shader = Shader()

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
        
        for obj in self.viewer.scene.objects:
            obj.init()

        # TODO(pitsai): impliment shader
        projection = self.camera.projection(self.w, self.h)
        viewworld = self.camera.viewworld()
        transform = list(identity(4, dtype=float32))

        self.shader_model = Shader(name="model")
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.uniform4x4("viewworld", viewworld)
        self.shader_model.uniform4x4("transform", transform)
        self.shader_model.uniform1i("is_selected", 0)
        self.shader_model.uniform1f("opacity", 1)
        self.shader_model.uniform3f("selection_color", Color.black())
        self.shader_model.release()

    def paintGL(self, is_instance: bool = False):
        pass

    def resizeGL(self, w: int, h: int):
        GL.glViewport(0, 0, self.viewer.config.window.width, self.viewer.config.window.height)
        # Add rendering code here

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
        mesh_objs = self.viewer.scene.sort_objects_from_category("MeshObject")

        # Draw model objects in the scene
        self.shader_model.bind()
        self.shader_model.uniform4x4("viewworld", viewworld)
        for obj in self.sort_objects_from_viewworld(mesh_objs, viewworld):
            obj.draw(self.shader_model, True, False)
        self.shader_model.release()

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
        w = w or self.viewer.config.window.width
        h = h or self.viewer.config.window.height

        projection = self.camera.projection(w, h)
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.release()

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
    
    def rotate(self, angle):
        self.rotation_angle += angle
        self.update()

    def zoom(self, factor):
        self.scale += factor
        self.update()



class View3D(OpenGLWidget):
    def __init__(self):
        super().__init__()
        self.controller = View3dController(self)
        self.installEventFilter(self.controller)
        # TODO(pitsai): config
        self.w = 1280
        self.h = 720
        self.opacity = 0.8
        self.selector_color = Color.yellow()
        self.shader_model = None
   
    def eventFilter(self, obj, event):
        if obj == self.opengl_view and event.type() in [event.MouseMove, event.Wheel]:
            # Redirect events to the controller
            self.controller.mouseMoveEvent(event) if event.type() == event.MouseMove else self.controller.wheelEvent(event)
            return True
        return super().eventFilter(obj, event)
