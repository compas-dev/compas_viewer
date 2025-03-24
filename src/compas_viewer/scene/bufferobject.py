from typing import Optional

import numpy as np
from numpy import array
from numpy import identity
from numpy.typing import NDArray

from compas.colors import Color
from compas.geometry import Geometry
from compas.scene import SceneObject
from compas_viewer.base import Base
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer
from compas_viewer.gl import update_vertex_buffer
from compas_viewer.renderer.shaders import Shader


class AttributeBuffer:
    """The buffer for the attributes of the object.

    Parameters
    ----------
    positions : Optional[NDArray], optional
        The flat list for vertex positions, in the form of [x1, y1, z1, x2, y2, z2, ...].
    colors : Optional[NDArray], optional
        The flat list for vertex colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].
    defaultcolor : Optional[Color], optional
        The default color for the vertices, if colors is not provided.
    dynamic : bool, optional
        Whether the buffer is dynamic or not.

    Attributes
    ----------
    positions : int
        The vertex buffer ID for the positions.
    colors : int
        The vertex buffer ID for the colors.
    elements : int
        The index buffer ID for the elements.
    elements_reversed : int
        The index buffer ID for the reversed elements (such as backfaces).
    n : int
        The number of elements.

    """

    def __init__(self, positions: Optional[NDArray] = None, colors: Optional[NDArray] = None, defaultcolor: Optional[Color] = None, dynamic: bool = True) -> None:
        positions = array([], dtype=float) if positions is None else positions.ravel()
        defaultcolor = defaultcolor or [0.8, 0.8, 0.8, 1.0]
        colors = np.full((positions.shape[0] // 3, 4), defaultcolor, dtype=float).ravel() if colors is None else colors.ravel()
        elements = np.arange(positions.shape[0] // 3, dtype=int)

        self.n = len(elements)
        self.positions = make_vertex_buffer(positions, dynamic)
        self.colors = make_vertex_buffer(colors, dynamic)
        self.elements = make_index_buffer(elements, dynamic)
        self.elements_reversed = make_index_buffer(np.flip(elements, axis=0), dynamic)

    def update(self, positions: Optional[NDArray] = None, colors: Optional[NDArray] = None) -> None:
        """Update the buffer with new data.

        Parameters
        ----------
        positions : Optional[NDArray], optional
            The flat list for vertex positions, in the form of [x1, y1, z1, x2, y2, z2, ...].
        colors : Optional[NDArray], optional
            The flat list for vertex colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].

        Returns
        -------
        None

        """
        if positions is not None:
            update_vertex_buffer(positions.ravel(), self.positions)
        if colors is not None:
            update_vertex_buffer(colors.ravel(), self.colors)


class BufferGeometry(Geometry):
    """A geometry defined directly from the buffer data.

    Parameters
    ----------
    points : Optional[NDArray], optional
        The flat list of point locations, in the form of [x1, y1, z1, x2, y2, z2, ...].
    lines : Optional[NDArray], optional
        The flat list of line segment vertices, in the form of [x1, y1, z1, x2, y2, z2, ...].
    faces : Optional[NDArray], optional
        The flat list of face vertices, in the form of [x1, y1, z1, x2, y2, z2, ...].
    pointcolor : Optional[NDArray], optional
        The flat list of point colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].
    linecolor : Optional[NDArray], optional
        The flat list of line vertices colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].
    facecolor : Optional[NDArray], optional
        The flat list of face vertices colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].

    Attributes
    ----------
    points : NDArray
        The flat list of point locations, in the form of [x1, y1, z1, x2, y2, z2, ...].
    lines : NDArray
        The flat list of line segment vertices, in the form of [x1, y1, z1, x2, y2, z2, ...].
    faces : NDArray
        The flat list of face vertices, in the form of [x1, y1, z1, x2, y2, z2, ...].
    pointcolor : NDArray
        The flat list of point colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].
    linecolor : NDArray
        The flat list of line vertices colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].
    facecolor : NDArray
        The flat list of face vertices colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].

    """

    def __init__(
        self,
        points: Optional[NDArray] = None,
        lines: Optional[NDArray] = None,
        faces: Optional[NDArray] = None,
        pointcolor: Optional[NDArray] = None,
        linecolor: Optional[NDArray] = None,
        facecolor: Optional[NDArray] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.points = points
        self.lines = lines
        self.faces = faces
        self.pointcolor = pointcolor
        self.linecolor = linecolor
        self.facecolor = facecolor


class BufferObject(SceneObject, Base):
    """The SceneObject for the BufferGeometry.

    Parameters
    ----------
    buffergeometry : BufferGeometry
        The buffer geometry to be displayed.
    show_points : Optional[bool], optional
        Whether to show the points or not.
    show_lines : Optional[bool], optional
        Whether to show the lines or not.
    show_faces : Optional[bool], optional
        Whether to show the faces or not.
    pointsize : Optional[float], optional
        The size of the points.
    linewidth : Optional[float], optional
        The width of the lines.
    opacity : Optional[float], optional
        The opacity of the object.
    doublesided : Optional[bool], optional
        Whether to show the backfaces or not.
    is_visiable : Optional[bool], optional
        Whether the object is visible or not.
    kwargs : dict
        Additional keyword arguments.

    Attributes
    ----------
    buffergeometry : BufferGeometry
        The buffer geometry to be displayed.
    show_points : bool
        Whether to show the points or not.
    show_lines : bool
        Whether to show the lines or not.
    show_faces : bool
        Whether to show the faces or not.
    pointsize : float
        The size of the points.
    linewidth : float
        The width of the lines.
    opacity : float
        The opacity of the object.
    doublesided : bool
        Whether to show the backfaces or not.
    is_visible : bool
        Whether the object is visible or not.
    is_selected : bool
        Whether the object is selected or not.
    background : bool
        Whether the object is in the background or not.


    """

    def __init__(
        self,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        show_faces: Optional[bool] = None,
        pointsize: Optional[float] = None,
        linewidth: Optional[float] = None,
        opacity: Optional[float] = None,
        doublesided: Optional[bool] = None,
        is_visiable: Optional[bool] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.show_points = True if show_points is None else show_points
        self.show_lines = True if show_lines is None else show_lines
        self.show_faces = True if show_faces is None else show_faces
        self.pointsize = 10.0 if pointsize is None else pointsize
        self.linewidth = 1.0 if linewidth is None else linewidth
        self.opacity = 1.0 if opacity is None else opacity
        self.doublesided = True if doublesided is None else doublesided
        self.show = True if is_visiable is None else is_visiable

        self.is_selected = False
        self.background = False
        self._bounding_box = None
        self._bounding_box_center = None

    @property
    def buffergeometry(self) -> BufferGeometry:
        return self.item

    @property
    def bounding_box(self) -> NDArray:
        if self._bounding_box is None:
            self._bounding_box = np.array([np.min(self.buffergeometry.points, axis=0), np.max(self.buffergeometry.points, axis=0)])
        return self._bounding_box

    @property
    def bounding_box_center(self) -> NDArray:
        if self._bounding_box_center is None:
            self._bounding_box_center = np.mean(self.buffergeometry.points.reshape(-1, 3), axis=0)
        return self._bounding_box_center

    def _update_bounding_box(self):
        self._bounding_box = None
        self._bounding_box_center = None
        # Set to None so that they are recalculated next time they are accessed

    def init(self):
        """Initialize the object"""
        self.instance_color = Color.from_rgb255(*next(self.scene._instance_colors_generator))
        self.scene.instance_colors[self.instance_color.rgb255] = self
        self.make_buffers()

    def update(self):
        """Update the object"""
        self.update_buffers()

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
        """Update the buffers for the object"""
        self.pointsbuffer.update(
            positions=self.buffergeometry.points,
            colors=self.buffergeometry.pointcolor,
        )
        self.linesbuffer.update(
            positions=self.buffergeometry.lines,
            colors=self.buffergeometry.linecolor,
        )
        self.facesbuffer.update(
            positions=self.buffergeometry.faces,
            colors=self.buffergeometry.facecolor,
        )

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
        if not wireframe and self.show_faces and self.doublesided:
            shader.bind_attribute("position", self.facesbuffer.positions)
            shader.bind_attribute("color", self.facesbuffer.colors, step=4)
            shader.draw_triangles(elements=self.facesbuffer.elements_reversed, n=self.facesbuffer.n, background=self.background)
        shader.uniform1i("is_lighted", False)
        shader.uniform1i("element_type", 1)
        # Lines
        if self.show_lines or wireframe:
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
        shader.enable_attribute("position")
        shader.uniform3f("instance_color", self.instance_color.rgb)
        # Matrix
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", self._matrix_buffer)
        # Points
        if self.show_points:
            shader.bind_attribute("position", self.pointsbuffer.positions)
            shader.draw_points(size=self.pointsize, elements=self.pointsbuffer.elements, n=self.pointsbuffer.n)
        # Lines
        if self.show_lines or wireframe:
            shader.bind_attribute("position", self.linesbuffer.positions)
            shader.draw_lines(
                width=self.linewidth + self.viewer.renderer.PIXEL_SELECTION_INCREMENTAL,
                elements=self.linesbuffer.elements,
                n=self.linesbuffer.n,
            )
        # Frontfaces
        if not wireframe and self.show_faces:
            shader.bind_attribute("position", self.facesbuffer.positions)
            shader.draw_triangles(elements=self.facesbuffer.elements, n=self.facesbuffer.n)
        # Backfaces
        if not wireframe and self.show_faces and self.doublesided:
            shader.bind_attribute("position", self.facesbuffer.positions)
            shader.draw_triangles(elements=self.facesbuffer.elements_reversed, n=self.facesbuffer.n)
        # Reset
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", identity(4).flatten())
        shader.uniform3f("instance_color", [0, 0, 0])
        shader.disable_attribute("position")
