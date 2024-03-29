from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import transform_points_numpy
from compas.scene import SceneObject
from compas.utilities import flatten
from numpy import array
from numpy import average
from numpy import identity

from compas_viewer.components.renderer.shaders import Shader
from compas_viewer.utilities.gl import make_index_buffer
from compas_viewer.utilities.gl import make_vertex_buffer
from compas_viewer.utilities.gl import update_index_buffer
from compas_viewer.utilities.gl import update_vertex_buffer

if TYPE_CHECKING:
    from compas_viewer import Viewer


# Type template of point/line/face data for generating the buffers.
ShaderDataType = tuple[list[Point], list[Color], list[list[int]]]


class ViewerSceneObject(SceneObject):
    """
    Base class for all Viewer scene objects
    which also includes the  GL buffer creation and drawing methods.

    Parameters
    ----------
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer object.
    is_selected : bool, optional
        Whether the object is selected. Default is False.
    is_locked : bool, optional
        Whether the object is locked. Default is False.
    is_visible : bool, optional
        Whether to show object. Default is True.
    show_points : bool, optional
        Whether to show points/vertices of the object. Default is the value of `show_points` in `viewer.config`.
    show_lines : bool, optional
        Whether to show lines/edges of the object. Default is the value of `show_lines` in `viewer.config`.
    show_faces : bool, optional
        Whether to show faces of the object. Default is the value of `show_faces` in `viewer.config`.
    lineswidth : float, optional
        The line width to be drawn on screen. Default is the value of `lineswidth` in `viewer.config`.
    pointssize : float, optional
        The point size to be drawn on screen. Default is the value of `pointssize` in `viewer.config`.
    opacity : float, optional
        The opacity of the object. Default is the value of `opacity` in `viewer.config`.
    **kwargs : dict, optional
        Additional visualization options for :class:`compas.scene.SceneObject`.

    Attributes
    ----------
    is_selected : boolA
        Whether the object is selected.
    is_locked : bool
        Whether the object is locked (selectable).
        The global grid is a typical object that is not selectable.
    is_visible : bool
        Whether to show object.
    show_points : bool
        Whether to show points/vertices of the object.
    show_lines : bool
        Whether to show lines/edges of the object.
    show_faces : bool
        Whether to show faces of the object.
    lineswidth : float
        The line width to be drawn on screen
    pointssize : float
        The point size to be drawn on screen.
    opacity : float
        The opacity of the object.
    background : bool
        Whether the object is drawn on the background with depth test disabled.
    bounding_box : list[float], read-only
        The min and max corners of object bounding box, as a numpy array of shape (2, 3).
    bounding_box_center : :class:`compas.geometry.Point`, read-only
        The center of object bounding box, as a point.

    See Also
    --------
    :class:`compas.scene.SceneObject`
    """

    def __init__(
        self,
        viewer: "Viewer",
        is_selected: bool = False,
        is_locked: bool = False,
        is_visible: bool = True,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        show_faces: Optional[bool] = None,
        lineswidth: Optional[float] = None,
        pointssize: Optional[float] = None,
        opacity: Optional[float] = None,
        use_rgba: bool = False,
        **kwargs,
    ):
        #  Basic
        super().__init__(**kwargs)
        self.viewer = viewer
        self.scene = viewer.scene
        self.renderer = viewer.renderer
        self.is_visible = is_visible
        self.show_points = self.viewer.config.show_points if show_points is None else show_points
        self.show_lines = self.viewer.config.show_lines if show_lines is None else show_lines
        self.show_faces = self.viewer.config.show_faces if show_faces is None else show_faces
        self.lineswidth = lineswidth or self.viewer.config.lineswidth
        self.pointssize = pointssize or self.viewer.config.pointssize
        self.opacity = opacity or self.viewer.config.opacity

        #  Selection
        self._is_locked = is_locked
        self.is_selected = not is_locked and is_selected
        self.instance_color = Color.from_rgb255(*next(self.scene._instance_colors_generator))
        if not is_locked:
            self.scene.instance_colors[self.instance_color.rgb255] = self

        #  Visual
        self.background: bool = False
        self.use_rgba = use_rgba

        #  Geometric
        self.transformation: Optional[Transformation] = None
        self._matrix_buffer: Optional[list[list[float]]] = None
        self._bounding_box: Optional[list[float]] = None
        self._bounding_box_center: Optional[Point] = None
        self._is_collection = False

        #  Primitive
        self._points_data: Optional[ShaderDataType] = None
        self._lines_data: Optional[ShaderDataType] = None
        self._frontfaces_data: Optional[ShaderDataType] = None
        self._backfaces_data: Optional[ShaderDataType] = None
        self._points_buffer: [dict[str, Any]] = None  # type: ignore
        self._lines_buffer: [dict[str, Any]] = None  # type: ignore
        self._frontfaces_buffer: [dict[str, Any]] = None  # type: ignore
        self._backfaces_buffer: [dict[str, Any]] = None  # type: ignore

    @property
    def is_locked(self):
        return self._is_locked

    @is_locked.setter
    def is_locked(self, value: bool):
        self._is_locked = value
        if value:
            self.is_selected = False
            self.scene.instance_colors.pop(self.instance_color.rgb255)
        else:
            self.scene.instance_colors[self.instance_color.rgb255] = self

    @property
    def bounding_box(self):
        return self._bounding_box

    @property
    def bounding_box_center(self):
        return self._bounding_box_center

    # ==========================================================================
    # Reading geometric data, downstream classes should implement these properties.
    # ==========================================================================

    def _read_points_data(self) -> Optional[ShaderDataType]:
        """Read points data from the object."""
        raise NotImplementedError

    def _read_lines_data(self) -> Optional[ShaderDataType]:
        """Read lines data from the object."""
        raise NotImplementedError

    def _read_frontfaces_data(self) -> Optional[ShaderDataType]:
        """Read frontfaces data from the object."""
        raise NotImplementedError

    def _read_backfaces_data(self) -> Optional[ShaderDataType]:
        """Read backfaces data from the object."""
        raise NotImplementedError

    # ==========================================================================
    # general
    # ==========================================================================

    def _update_matrix(self):
        """Update the matrix from object's translation, rotation and scale"""
        if self.transformation is not None:
            self._matrix_buffer = list(array(self.worldtransformation.matrix).flatten())

        if self.children:
            for child in self.children:
                child._update_matrix()

    # ==========================================================================
    # buffer
    # ==========================================================================

    def make_buffer_from_data(self, data: ShaderDataType) -> dict[str, Any]:
        """Create buffers from point/line/face data.

        Parameters
        ----------
        data : tuple[list[:class:`compas.geometry.Point`], list[:class:`compas.colors.Color`], list[int]]
            Contains positions, colors, elements for the buffer.

        Returns
        -------
        buffer_dict : dict[str, Any]
            A dict with created buffer indexes.
        """
        if len(data) == 3:
            positions, colors, elements = data
            return {
                "positions": make_vertex_buffer(list(flatten(positions))),
                "colors": make_vertex_buffer(list(flatten(colors))),
                "elements": make_index_buffer(list(flatten(elements))),
                "n": len(list(flatten(elements))),
            }
        elif len(data) == 4:
            positions, colors, opacities, elements = data
            return {
                "positions": make_vertex_buffer(list(flatten(positions))),
                "colors": make_vertex_buffer(list(flatten(colors))),
                "opacities": make_vertex_buffer(opacities),
                "elements": make_index_buffer(list(flatten(elements))),
                "n": len(list(flatten(elements))),
            }

    def update_buffer_from_data(
        self,
        data: ShaderDataType,
        buffer: dict[str, Any],
        update_positions: bool,
        update_colors: bool,
        update_elements: bool,
    ):
        """Update existing buffers from point/line/face data.

        Parameters
        ----------
        data : tuple[list[:class:`compas.geometry.Point`], list[:class:`compas.colors.Color`], list[int]]
            Contains positions, colors, elements for the buffer.
        buffer : dict[str, Any]
            The dict with created buffer indexes
        update_positions : bool
            Whether to update positions in the buffer dict.
        update_colors : bool
            Whether to update colors in the buffer dict.
        update_elements : bool
            Whether to update elements in the buffer dict.
        """
        positions, colors, elements = data
        if update_positions:
            update_vertex_buffer(list(flatten(positions)), buffer["positions"])
        if update_colors:
            update_vertex_buffer(list(flatten(colors)), buffer["colors"])
        if update_elements:
            update_index_buffer(list(flatten(elements)), buffer["elements"])
        buffer["n"] = len(list(flatten(elements)))

    def make_buffers(self):
        """Create all buffers from object's data"""
        if self._points_data is not None:
            data = self._points_data
            self._points_buffer = self.make_buffer_from_data(data)
            if len(data[0]):
                self._update_bounding_box(data[0])
        if self._lines_data is not None:
            data = self._lines_data
            self._lines_buffer = self.make_buffer_from_data(data)
            if len(data[0]) and self._bounding_box_center is None:
                self._update_bounding_box(data[0])
        if self._frontfaces_data is not None:
            data = self._frontfaces_data
            self._frontfaces_buffer = self.make_buffer_from_data(data)
            if len(data[0]) and self._bounding_box_center is None:
                self._update_bounding_box(data[0])
        if self._backfaces_data is not None:
            data = self._backfaces_data
            self._backfaces_buffer = self.make_buffer_from_data(data)
            if len(data[0]) and self._bounding_box_center is None:
                self._update_bounding_box(data[0])

    def update_buffers(self):
        """Update all buffers from object's data"""

        if self._points_data is not None:
            # boolean values are keys for improving the performance, true for now to update all, will flag them later.
            self.update_buffer_from_data(self._points_data, self._points_buffer, True, True, True)
        if self._lines_data is not None:
            self.update_buffer_from_data(self._lines_data, self._lines_buffer, True, True, True)
        if self._frontfaces_data is not None:
            self.update_buffer_from_data(self._frontfaces_data, self._frontfaces_buffer, True, True, True)
        if self._backfaces_data is not None:
            self.update_buffer_from_data(self._backfaces_data, self._backfaces_buffer, True, True, True)

    def init(self):
        """Initialize the object"""
        self._points_data = self._read_points_data() if self.show_points else None
        self._lines_data = self._read_lines_data() if self.show_lines else None
        self._frontfaces_data = self._read_frontfaces_data() if self.show_faces else None
        self._backfaces_data = self._read_backfaces_data() if self.show_faces else None
        self.make_buffers()
        self._update_matrix()

    def update(self):
        """Update the object"""
        self._update_matrix()
        self.update_buffers()
        self.renderer.update()

    def _update_bounding_box(self, positions: Optional[list[Point]] = None):
        """Update the bounding box of the object"""
        if positions is None:
            positions = []
            if self._points_data is not None:
                positions += self._points_data[0]
            if self._lines_data is not None:
                positions += self._lines_data[0]
            if self._frontfaces_data is not None:
                positions += self._frontfaces_data[0]
            if not positions:
                return

        _positions = array(positions)
        self._bounding_box = list(
            transform_points_numpy(array([_positions.min(axis=0), _positions.max(axis=0)]), self.worldtransformation)
        )
        self._bounding_box_center = Point(*list(average(a=array(self.bounding_box), axis=0)))

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
        if self.use_rgba:
            shader.enable_attribute("alpha")
        shader.uniform1i("use_rgba", self.use_rgba)
        if self._frontfaces_buffer is not None and not wireframe:
            shader.bind_attribute("position", self._frontfaces_buffer["positions"])
            shader.bind_attribute("color", self._frontfaces_buffer["colors"])
            if self.use_rgba and self._frontfaces_buffer.get("opacities") is not None:
                shader.bind_attribute("alpha", self._frontfaces_buffer["opacities"], step=1)
            shader.draw_triangles(
                elements=self._frontfaces_buffer["elements"], n=self._frontfaces_buffer["n"], background=self.background
            )
        # Backfaces
        if self._backfaces_buffer is not None and not wireframe:
            shader.bind_attribute("position", self._backfaces_buffer["positions"])
            shader.bind_attribute("color", self._backfaces_buffer["colors"])
            if self.use_rgba and self._backfaces_buffer.get("opacities") is not None:
                shader.bind_attribute("alpha", self._backfaces_buffer["opacities"], step=1)
            shader.draw_triangles(
                elements=self._backfaces_buffer["elements"], n=self._backfaces_buffer["n"], background=self.background
            )
        shader.uniform1i("is_lighted", False)
        shader.uniform1i("element_type", 1)
        # Lines
        if self._lines_buffer is not None:
            shader.bind_attribute("position", self._lines_buffer["positions"])
            shader.bind_attribute("color", self._lines_buffer["colors"])
            shader.draw_lines(
                width=self.lineswidth,
                elements=self._lines_buffer["elements"],
                n=self._lines_buffer["n"],
                background=self.background,
            )
        shader.uniform1i("element_type", 0)
        # Points
        if self._points_buffer is not None:
            shader.bind_attribute("position", self._points_buffer["positions"])
            shader.bind_attribute("color", self._points_buffer["colors"])
            shader.draw_points(
                size=self.pointssize,
                elements=self._points_buffer["elements"],
                n=self._points_buffer["n"],
                background=self.background,
            )
        # Reset
        shader.uniform1i("is_selected", 0)
        shader.uniform1f("object_opacity", 1)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", list(identity(4).flatten()))
        shader.disable_attribute("position")
        shader.disable_attribute("color")
        if self.use_rgba:
            shader.disable_attribute("alpha")

    def draw_instance(self, shader, wireframe: bool):
        """Draw the object instance for picking"""
        shader.enable_attribute("position")
        shader.uniform3f("instance_color", self.instance_color.rgb)
        # Matrix
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", self._matrix_buffer)
        # Points
        if self._points_buffer is not None and self.show_points:
            shader.bind_attribute("position", self._points_buffer["positions"])
            shader.draw_points(
                size=self.pointssize, elements=self._points_buffer["elements"], n=self._points_buffer["n"]
            )
        # Lines
        if self._lines_buffer is not None and (self.show_lines or wireframe):
            shader.bind_attribute("position", self._lines_buffer["positions"])
            shader.draw_lines(
                width=self.lineswidth + self.renderer.selector.PIXEL_SELECTION_INCREMENTAL,
                elements=self._lines_buffer["elements"],
                n=self._lines_buffer["n"],
            )
        # Frontfaces
        if self._frontfaces_buffer is not None and not wireframe:
            shader.bind_attribute("position", self._frontfaces_buffer["positions"])
            shader.draw_triangles(elements=self._frontfaces_buffer["elements"], n=self._frontfaces_buffer["n"])
        # Backfaces
        if self._backfaces_buffer is not None and not wireframe:
            shader.bind_attribute("position", self._backfaces_buffer["positions"])
            shader.draw_triangles(elements=self._backfaces_buffer["elements"], n=self._backfaces_buffer["n"])
        # Reset
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", identity(4).flatten())
        shader.uniform3f("instance_color", [0, 0, 0])
        shader.disable_attribute("position")
