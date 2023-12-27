from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Transformation
from compas.geometry import Translation
from compas.geometry import decompose_matrix
from compas.geometry import identity_matrix
from compas.geometry import transform_points_numpy
from compas.scene import SceneObject
from compas.utilities import flatten

from compas_viewer.utilities.gl import make_index_buffer
from compas_viewer.utilities.gl import make_vertex_buffer
from compas_viewer.utilities.gl import update_index_buffer
from compas_viewer.utilities.gl import update_vertex_buffer
from compas_viewer.configurations import SceneConfig

if TYPE_CHECKING:
    from compas_viewer import Viewer
    from compas_viewer.components.render.shaders import Shader


class ViewerSceneObject(SceneObject):
    """Base class for all Viewer scene objects
    which also includes the  GL buffer creation and drawing methods.

    Parameters
    ----------
    name : str, optional
        The name of the object.
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer object.
    is_selected : bool
        Whether the object is selected.
    is_visible : bool
        Whether to show object.
    show_points : bool, optional
        Whether to show points/vertices of the object. It will override the value in the config file.
    show_lines : bool, optional
        Whether to show lines/edges of the object. It will override the value in the config file.
    show_faces : bool, optional
        Whether to show faces of the object. It will override the value in the config file.
    pointscolor : Union[:class:`compas.colors.Color`, dict[any, :class:`compas.colors.Color`]], optional
        The color or the dict of colors of the points. It will override the value in the config file.
    linescolor : Union[:class:`compas.colors.Color`, dict[any, :class:`compas.colors.Color`]], optional
        The color or the dict of colors of the lines. It will override the value in the config file.
    facescolor : Union[:class:`compas.colors.Color`, dict[any, :class:`compas.colors.Color`]], optional
        The color or the dict of colors the faces. It will override the value in the config file.
    lineswidth : float, optional
        The line width to be drawn on screen. It will override the value in the config file.
    pointssize : float, optional
        The point size to be drawn on screen. It will override the value in the config file.
    opacity : float, optional
        The opacity of the object. It will override the value in the config file.
    config: :class:`compas_viewer.configurations.SceneConfig`.
        The configuration of the scene object. Defaults to None.
        It should be assigned though the :class:`compas_viewer.viewer.Viewer.add` method.
        Otherwise a exception will be raised.
    **kwargs : dict, optional
        Additional visualization options for specific objects.

    Attributes
    ----------
    name : str
        The name of the object.
    is_selected : bool
        Whether the object is selected.
    is_visible : bool
        Whether to show object.
    show_points : bool
        Whether to show points/vertices of the object.
    show_lines : bool
        Whether to show lines/edges of the object.
    show_faces : bool
        Whether to show faces of the object.
    pointscolor : dict[Any, :class:`compas.colors.Color`]
        The color of the points.
    linescolor : dict[Any, :class:`compas.colors.Color`]
        The color of the lines.
    facescolor : dict[Any, :class:`compas.colors.Color`]
        The color of the faces.
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
    matrix : list[float], read-only
        The transformation matrix of the object.
    translation : :class:`compas.geometry.Translation`
        The translation of the object.
    rotation : :class:`compas.geometry.Rotation`
        The euler rotation  of the object.
    scale : :class:`compas.geometry.Scale`
        The scale of the object.
    properties : list, read-only
        The list of object-specific properties.
    visualisation : list[str], read-only
        List of visualisation properties which can be edited in the GUI.
    """

    def __init__(
        self,
        name: Optional[str],
        viewer: "Viewer",
        is_selected: bool,
        is_visible: bool,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        show_faces: Optional[bool] = None,
        pointscolor: Optional[Union[Color, Dict[Any, Color]]] = None,
        linescolor: Optional[Union[Color, Dict[Any, Color]]] = None,
        facescolor: Optional[Union[Color, Dict[Any, Color]]] = None,
        lineswidth: Optional[float] = None,
        pointssize: Optional[float] = None,
        opacity: Optional[float] = None,
        config: Optional[SceneConfig] = None,
        **kwargs,
    ):
        if config is None:
            raise ValueError(
                "No SceneConfig specified for the ViewerSceneObject. "
                + "Check if the object is added by the function `Viewer.add`."
            )
        self.config = config
        super(ViewerSceneObject, self).__init__(config=self.config, **kwargs)
        self.name = name or str(self)
        self.is_selected = is_selected
        self.is_visible = is_visible
        self.viewer = viewer
        self.parent: Optional[ViewerSceneObject] = None
        self._children = set()

        self.show_points = show_points if show_points is not None else self.config.show_points
        self.show_lines = show_lines if show_lines is not None else self.config.show_lines
        self.show_faces = show_faces if show_faces is not None else self.config.show_faces

        if pointscolor is None:
            self.pointscolor = {"_default": self.config.pointscolor}
        elif isinstance(pointscolor, Color):
            self.pointscolor = {"_default": pointscolor}
        else:
            self.pointscolor = pointscolor
            self.pointscolor["_default"] = self.config.pointscolor

        if linescolor is None:
            self.linescolor = {"_default": self.config.linescolor}
        elif isinstance(linescolor, Color):
            self.linescolor = {"_default": linescolor}
        else:
            self.linescolor = linescolor
            self.linescolor["_default"] = self.config.linescolor

        if facescolor is None:
            self.facescolor = {"_default": self.config.facescolor}
        elif isinstance(facescolor, Color):
            self.facescolor = {"_default": facescolor}
        else:
            self.facescolor = facescolor
            self.facescolor["_default"] = self.config.facescolor

        self.lineswidth = lineswidth or self.config.lineswidth
        self.pointssize = pointssize or self.config.pointssize
        self.opacity = opacity or self.config.opacity
        self.background: bool = False

        self._instance_color: Optional[Color] = None
        self._translation = Translation.from_matrix([0.0, 0.0, 0.0])
        self._rotation = Rotation.from_matrix([0.0, 0.0, 0.0])
        self._scale = Scale.from_matrix([1.0, 1.0, 1.0])
        self._transformation = Transformation.from_matrix(identity_matrix(4))
        self._matrix_buffer: Optional[List[List[float]]] = None

        self._bounding_box: Optional[List[float]] = None
        self._bounding_box_center: Optional[Point] = None
        self._is_collection = False

        self._points_data: Optional[Tuple[List[Point], List[Color], List[int]]]
        self._lines_data: Optional[Tuple[List[Point], List[Color], List[int]]]
        self._frontfaces_data: Optional[Tuple[List[Point], List[Color], List[int]]]
        self._backfaces_data: Optional[Tuple[List[Point], List[Color], List[int]]]
        self._points_buffer: Optional[Dict[str, Any]] = None
        self._lines_buffer: Optional[Dict[str, Any]] = None
        self._frontfaces_buffer: Optional[Dict[str, Any]] = None
        self._backfaces_buffer: Optional[Dict[str, Any]] = None

    @property
    def bounding_box(self):
        return self._bounding_box

    @property
    def bounding_box_center(self):
        return self._bounding_box_center

    @property
    def children(self):
        return self._children

    @property
    def properties(self):
        return None

    # ==========================================================================
    # general
    # ==========================================================================

    # TODO
    # def add(self, item, **kwargs):
    #     if isinstance(item, Object):
    #         obj = item
    #     else:
    #         obj = self._app.add(item, **kwargs)
    #     self._children.add(obj)
    #     obj.parent = self

    #     if self._app.dock_slots["sceneform"] and self._app.view.isValid():
    #         self._app.dock_slots["sceneform"].update()
    #     return obj

    def remove(self, obj):
        obj.parent = None
        self._children.remove(obj)

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, vector):
        self._translation[0] = vector[0]
        self._translation[1] = vector[1]
        self._translation[2] = vector[2]

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, angles):
        self._rotation[0] = angles[0]
        self._rotation[1] = angles[1]
        self._rotation[2] = angles[2]

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, factors):
        self._scale[0] = factors[0]
        self._scale[1] = factors[1]
        self._scale[2] = factors[2]

    def _update_matrix(self):
        """Update the matrix from object's translation, rotation and scale"""
        if (not self.parent or self.parent._matrix_buffer is None) and (
            self.translation.matrix == [0, 0, 0]
            and self.rotation.matrix == [0, 0, 0]
            and self.scale.matrix == [1, 1, 1]
        ):
            self._transformation.matrix = identity_matrix(4)
            self._matrix_buffer = None
        else:
            M = self.translation * self.rotation * self.scale
            self._transformation.matrix = M.matrix
            self._matrix_buffer = list(np.array(self.matrix_world).flatten())

        if self.children:
            for child in self.children:
                child._update_matrix()

    @property
    def transformation(self):
        return self._transformation

    @property
    def transformation_world(self):
        """Get the updated matrix from object's translation, rotation and scale"""
        if self.parent:
            assert isinstance(self.parent.transformation_world, Transformation)
            return self.parent.transformation_world * self.transformation
        else:
            return self.transformation

    @property
    def matrix(self):
        """Get the updated matrix from object's translation, rotation and scale"""
        return self.transformation.matrix

    @property
    def matrix_world(self):
        """Get the updated matrix from object's translation, rotation and scale"""
        return self.transformation_world.matrix

    @matrix.setter
    def matrix(self, matrix):
        """Set the object's translation, rotation and scale from given matrix, and update object's matrix"""
        scale, _, rotation, translation, _ = decompose_matrix(matrix)
        self.translation = translation
        self.rotation = rotation
        self.scale = scale
        self._update_matrix()

    # ==========================================================================
    # buffer
    # ==========================================================================

    @property
    def visualisation(self) -> List[str]:
        """List of visualisation properties which can be edited in the GUI."""
        options = ["opacity"]
        if self._points_data is not None:
            options += ["pointscolor", "show_points", "pointssize"]
        if self._lines_data is not None:
            options += ["linescolor", "show_lines", "lineswidth"]
        if self._frontfaces_data is not None:
            options += ["facescolor", "show_faces"]
        return options

    def make_buffer_from_data(self, data: Tuple[List[Point], List[Color], List[int]]) -> Dict[str, Any]:
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
        positions, colors, elements = data
        return {
            "positions": make_vertex_buffer(list(flatten(positions))),
            "colors": make_vertex_buffer(list(flatten(colors))),
            "elements": make_index_buffer(list(flatten(elements))),
            "n": len(list(flatten(elements))),
        }

    def update_buffer_from_data(
        self,
        data: Tuple[List[Point], List[Color], List[int]],
        buffer: Dict[str, Any],
        update_positions: bool = True,
        update_colors: bool = True,
        update_elements: bool = True,
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
            if data[0]:
                self._update_bounding_box(data[0])
        if self._lines_data is not None:
            data = self._lines_data
            self._lines_buffer = self.make_buffer_from_data(data)
            if data[0] and self._bounding_box_center is None:
                self._update_bounding_box(data[0])
        if self._frontfaces_data is not None:
            data = self._frontfaces_data
            self._frontfaces_buffer = self.make_buffer_from_data(data)
            if data[0] and self._bounding_box_center is None:
                self._update_bounding_box(data[0])
        if self._backfaces_data is not None:
            data = self._backfaces_data
            self._backfaces_buffer = self.make_buffer_from_data(data)
            if data[0] and self._bounding_box_center is None:
                self._update_bounding_box(data[0])

    def update_buffers(self):
        """Update all buffers from object's data"""

        if self._points_data is not None:
            assert self._points_buffer is not None
            self.update_buffer_from_data(self._points_data, self._points_buffer)
        if self._lines_data is not None:
            assert self._lines_buffer is not None
            self.update_buffer_from_data(self._lines_data, self._lines_buffer)
        if self._frontfaces_data is not None:
            assert self._frontfaces_buffer is not None
            self.update_buffer_from_data(self._frontfaces_data, self._frontfaces_buffer)
        if self._backfaces_data is not None:
            assert self._backfaces_buffer is not None
            self.update_buffer_from_data(self._backfaces_data, self._backfaces_buffer)

    def init(self):
        """Initialize the object"""
        self.make_buffers()
        self._update_matrix()

    def update(self):
        """Update the object"""
        self._update_matrix()
        self.update_buffers()

    def _update_bounding_box(self, positions=None):
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

        positions = np.array(positions)
        self._bounding_box = list(
            transform_points_numpy(np.array([positions.min(axis=0), positions.max(axis=0)]), self._transformation)
        )
        self._bounding_box_center = Point(*list(np.average(a=np.array(self.bounding_box), axis=0)))

    def draw(self, shader: "Shader", wireframe=False, is_lighted=False):
        """Draw the object from its buffers"""

        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.uniform1i("is_selected", self.is_selected)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", self._matrix_buffer)
        shader.uniform1i("is_lighted", is_lighted)
        shader.uniform1f("object_opacity", self.opacity)
        shader.uniform1i("element_type", 2)
        if self._frontfaces_buffer is not None and self.show_faces and not wireframe:
            shader.uniform3f("single_color", self.facescolor["_default"].rgb)
            shader.uniform1i(
                "use_single_color",
                not self.facescolor and not self._is_collection and not getattr(self, "use_vertexcolors", False),
            )
            shader.bind_attribute("position", self._frontfaces_buffer["positions"])
            shader.bind_attribute("color", self._frontfaces_buffer["colors"])
            shader.draw_triangles(
                elements=self._frontfaces_buffer["elements"], n=self._frontfaces_buffer["n"], background=self.background
            )
        if self._backfaces_buffer is not None and self.show_faces and not wireframe:
            shader.uniform3f("single_color", self.facescolor["_default"].rgb)
            shader.uniform1i(
                "use_single_color",
                not self.facescolor and not self._is_collection and not getattr(self, "use_vertexcolors", False),
            )
            shader.bind_attribute("position", self._backfaces_buffer["positions"])
            shader.bind_attribute("color", self._backfaces_buffer["colors"])
            shader.draw_triangles(
                elements=self._backfaces_buffer["elements"], n=self._backfaces_buffer["n"], background=self.background
            )
        shader.uniform1i("is_lighted", False)
        shader.uniform1i("element_type", 1)
        if self._lines_buffer is not None and (self.show_lines or wireframe):
            shader.uniform3f("single_color", self.linescolor["_default"].rgb)
            shader.uniform1i("use_single_color", not self.linescolor and not self._is_collection)
            shader.bind_attribute("position", self._lines_buffer["positions"])
            shader.bind_attribute("color", self._lines_buffer["colors"])
            shader.draw_lines(
                width=self.lineswidth,
                elements=self._lines_buffer["elements"],
                n=self._lines_buffer["n"],
                background=self.background,
            )
        shader.uniform1i("element_type", 0)
        if self._points_buffer is not None and self.show_points:
            shader.uniform3f("single_color", self.pointscolor["_default"].rgb)
            shader.uniform1i("use_single_color", not self.pointscolor and not self._is_collection)
            shader.bind_attribute("position", self._points_buffer["positions"])
            shader.bind_attribute("color", self._points_buffer["colors"])
            shader.draw_points(
                size=self.pointssize,
                elements=self._points_buffer["elements"],
                n=self._points_buffer["n"],
                background=self.background,
            )

        shader.uniform1i("is_selected", 0)
        shader.uniform1f("object_opacity", 1)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", list(np.identity(4).flatten()))
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def draw_instance(self, shader, wireframe=False):
        """Draw the object instance for picking"""
        shader.enable_attribute("position")
        shader.uniform3f("instance_color", self._instance_color)
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", self._matrix_buffer)
        if self._points_buffer is not None and self.show_points:
            shader.bind_attribute("position", self._points_buffer["positions"])
            shader.draw_points(
                size=self.pointssize, elements=self._points_buffer["elements"], n=self._points_buffer["n"]
            )
        if self._lines_buffer is not None and (self.show_lines or wireframe):
            shader.bind_attribute("position", self._lines_buffer["positions"])
            shader.draw_lines(width=self.lineswidth, elements=self._lines_buffer["elements"], n=self._lines_buffer["n"])
        if self._frontfaces_buffer is not None and self.show_faces and not wireframe:
            shader.bind_attribute("position", self._frontfaces_buffer["positions"])
            shader.draw_triangles(elements=self._frontfaces_buffer["elements"], n=self._frontfaces_buffer["n"])
            assert self._backfaces_buffer is not None
            shader.bind_attribute("position", self._backfaces_buffer["positions"])
            shader.draw_triangles(elements=self._backfaces_buffer["elements"], n=self._backfaces_buffer["n"])
        if self._matrix_buffer is not None:
            shader.uniform4x4("transform", np.identity(4).flatten())
        shader.uniform3f("instance_color", [0, 0, 0])
        shader.disable_attribute("position")

    def clear(self):
        """Clear the object"""
        raise NotImplementedError("clear() method is not implemented.")
