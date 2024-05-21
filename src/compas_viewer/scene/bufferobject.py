import numpy as np
from numpy import array
from numpy import identity

from compas.geometry import Geometry
from compas.scene import SceneObject
from compas_viewer.base import Base
from compas_viewer.components.renderer.shaders import Shader
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer


class AttributeBuffer:
    def __init__(self, positions=None, colors=None, defaultcolor=None, dynamic=False) -> None:
        if positions is None:
            positions = np.zeros((0, 3), dtype=float)
        else:
            positions = array(positions, dtype=float).reshape(-1, 3)

        if colors is None:
            defaultcolor = defaultcolor or [0.8, 0.8, 0.8, 1.0]
            colors = np.full((positions.shape[0], 4), defaultcolor, dtype=float)
        else:
            colors = array(colors)

        elements = np.arange(positions.shape[0], dtype=int)
        self.n = len(elements)

        self.dynamic = dynamic
        self.positions = make_vertex_buffer(positions.ravel(), dynamic)
        self.colors = make_vertex_buffer(colors.ravel(), dynamic)
        self.elements = make_index_buffer(elements.ravel(), dynamic)
        self.elements_reversed = make_index_buffer(np.flip(elements, axis=0).ravel(), dynamic)


class BufferGeometry(Geometry):
    def __init__(self, points=None, lines=None, faces=None, pointcolor=None, linecolor=None, facecolor=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.points = points
        self.lines = lines
        self.faces = faces
        self.pointcolor = pointcolor
        self.linecolor = linecolor
        self.facecolor = facecolor


class BufferObject(SceneObject, Base):
    """ """

    def __init__(self, buffergeometry: BufferGeometry, **kwargs):
        super().__init__(item=buffergeometry, **kwargs)
        self.buffergeometry = buffergeometry

        self.is_visible = True
        self.is_selected = False
        self.opacity = 1.0
        self._matrix_buffer = None

        self.show_points = True
        self.pointsize = 20
        self.show_lines = True
        self.linewidth = 1
        self.show_faces = True

        self.background = False

    def init(self):
        """Initialize the object"""
        self.make_buffers()

    def make_buffers(self):
        """Make the buffers for the object"""
        self.pointsbuffer = AttributeBuffer(
            positions=self.buffergeometry.points,
            colors=self.buffergeometry.pointcolor,
            defaultcolor=[0.0, 0.0, 0.0, 1.0],
        )

        self.linesbuffer = AttributeBuffer(
            positions=self.buffergeometry.lines,
            colors=self.buffergeometry.linecolor,
            defaultcolor=[0.5, 0.5, 0.5, 1.0],
        )

        self.facesbuffer = AttributeBuffer(
            positions=self.buffergeometry.faces,
            colors=self.buffergeometry.facecolor,
        )

    def update_buffers(self):
        raise NotImplementedError()

    def draw(self, shader: Shader, wireframe: bool, is_lighted: bool):
        """Draw the object from its buffers"""
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.uniform1i("is_selected", self.is_selected)
        # Matrix
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", self._matrix_buffer)
        shader.uniform1i("is_lighted", is_lighted)
        shader.uniform1f("object_opacity", self.opacity)
        shader.uniform1i("element_type", 2)
        # Frontfaces
        if not wireframe and self.show_faces:
            shader.bind_attribute("position", self.facesbuffer.positions)
            shader.bind_attribute("color", self.facesbuffer.colors, step=4)
            shader.draw_triangles(
                elements=self.facesbuffer.elements,
                n=self.facesbuffer.n,
                background=self.background,
            )
        # Backfaces
        if not wireframe and self.show_faces:
            shader.bind_attribute("position", self.facesbuffer.positions)
            shader.bind_attribute("color", self.facesbuffer.colors, step=4)
            shader.draw_triangles(elements=self.facesbuffer.elements_reversed, n=self.facesbuffer.n, background=self.background)
        shader.uniform1i("is_lighted", False)
        shader.uniform1i("element_type", 1)
        # Lines
        if self.show_lines:
            shader.bind_attribute("position", self.linesbuffer.positions)
            shader.bind_attribute("color", self.linesbuffer.colors, step=4)
            shader.draw_lines(
                width=self.linewidth,
                elements=self.linesbuffer.elements,
                n=self.linesbuffer.n,
                background=self.background,
            )
        shader.uniform1i("element_type", 0)
        # Points
        if self.show_points:
            shader.bind_attribute("position", self.pointsbuffer.positions)
            shader.bind_attribute("color", self.pointsbuffer.colors, step=4)
            shader.draw_points(
                size=self.pointsize,
                elements=self.pointsbuffer.elements,
                n=self.pointsbuffer.n,
                background=self.background,
            )
        # Reset
        shader.uniform1i("is_selected", 0)
        shader.uniform1f("object_opacity", 1)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", list(identity(4).flatten()))
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def draw_instance(self, shader, wireframe: bool):
        """Draw the object instance for picking"""
        pass
        # shader.enable_attribute("position")
        # shader.uniform3f("instance_color", self.instance_color.rgb)
        # # Matrix
        # if self._matrix_buffer is not None:
        #     shader.uniform4x4("transform", self._matrix_buffer)
        # # Points
        # if self._points_buffer is not None and self.show_points:
        #     shader.bind_attribute("position", self._points_buffer["positions"])
        #     shader.draw_points(size=self.pointsize, elements=self._points_buffer["elements"], n=self._points_buffer["n"])
        # # Lines
        # if self._lines_buffer is not None and (self.show_lines or wireframe):
        #     shader.bind_attribute("position", self._lines_buffer["positions"])
        #     shader.draw_lines(
        #         width=self.linewidth + self.viewer.renderer.selector.PIXEL_SELECTION_INCREMENTAL,
        #         elements=self._lines_buffer["elements"],
        #         n=self._lines_buffer["n"],
        #     )
        # # Frontfaces
        # if self._frontfaces_buffer is not None and not wireframe and self.show_faces:
        #     shader.bind_attribute("position", self._frontfaces_buffer["positions"])
        #     shader.draw_triangles(elements=self._frontfaces_buffer["elements"], n=self._frontfaces_buffer["n"])
        # # Backfaces
        # if self._backfaces_buffer is not None and not wireframe and self.show_faces:
        #     shader.bind_attribute("position", self._backfaces_buffer["positions"])
        #     shader.draw_triangles(elements=self._backfaces_buffer["elements"], n=self._backfaces_buffer["n"])
        # # Reset
        # if self._matrix_buffer is not None:
        #     shader.uniform4x4("transform", identity(4).flatten())
        # shader.uniform3f("instance_color", [0, 0, 0])
        # shader.disable_attribute("position")
