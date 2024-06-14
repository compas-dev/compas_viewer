from typing import Optional

from compas.colors import Color

from compas.scene.descriptors.color import ColorAttribute
from compas.scene.geometryobject import GeometryObject
from .bufferobject import BufferGeometry
from .bufferobject import BufferObject
from .sceneobject import ShaderDataType

from numpy import array


class ShapeObject(BufferObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Geometry.

    Parameters
    ----------
    geometry : :class:`compas.geometry.Geometry`
        A COMPAS geometry.
    v : int, optional
        The number of vertices in the u-direction of non-OCC geometries.
    u : int, optional
        The number of vertices in the v-direction of non-OCC geometries.
    pointcolor : :class:`compas.colors.Color`, optional
        The color of the points. Default is the value of `pointcolor` in `viewer.config`.
    linecolor : :class:`compas.colors.Color`, optional
        The color of the lines. Default is the value of `linecolor` in `viewer.config`.
    surfacecolor : :class:`compas.colors.Color`, optional
        The color of the surfaces. Default is the value of `surfacecolor` in `viewer.config`.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`
        and :class:`compas.scene.GeometryObject`.

    Attributes
    ----------
    geometry : :class:`compas.geometry.Geometry`
        The COMPAS geometry.
    pointcolor : :class:`compas.colors.Color`
        The color of the points.
    linecolor : :class:`compas.colors.Color`
        The color of the lines.
    surfacecolor : :class:`compas.colors.Color`
        The color of the surfaces.
    mesh : :class:`compas.datastructures.Mesh`
        The triangulated mesh representation of the geometry.
    LINEARDEFLECTION : float
        The default linear deflection for the geometry.

    See Also
    --------
    :class:`compas.geometry.Geometry`
    """

    pointcolor = ColorAttribute(default=Color(0.2, 0.2, 0.2))
    linecolor = ColorAttribute(default=Color(0.2, 0.2, 0.2))
    surfacecolor = ColorAttribute(default=Color(0.9, 0.9, 0.9))

    def __init__(
        self,
        u: Optional[int] = 16,
        v: Optional[int] = 16,
        show_points: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._buffergeometry = None
        self.u = u
        self.v = v
        self.show_points = show_points

    @property
    def u(self) -> int:
        return self.geometry.resolution_u

    @u.setter
    def u(self, u: int) -> None:
        self.geometry.resolution_u = u

    @property
    def v(self) -> int:
        return self.geometry.resolution_v

    @v.setter
    def v(self, v: int) -> None:
        self.geometry.resolution_v = v

    @property
    def facecolor(self) -> Color:
        return self.surfacecolor

    @facecolor.setter
    def facecolor(self, color: Color) -> None:
        self.surfacecolor = color

    @property
    def buffergeometry(self) -> BufferGeometry:

        if not self._buffergeometry:
            # TODO: might need to be cached here since vertices are always recomputed.
            vertices = self.geometry.vertices
            edges = self.geometry.edges
            faces = self.geometry.triangles
            pointcolor = [self.pointcolor.rgba] * len(vertices)
            linecolor = [self.linecolor.rgba] * len(edges) * 2
            facecolor = [self.facecolor.rgba] * len(faces) * 3
            self._buffergeometry = BufferGeometry(points=vertices, lineindices=edges, faceindices=faces, pointcolor=pointcolor, linecolor=linecolor, facecolor=facecolor)

        return self._buffergeometry

    # def _read_points_data(self) -> ShaderDataType:
    #     positions = self.geometry.vertices
    #     colors = [self.pointcolor] * len(positions)
    #     elements = [[i] for i in range(len(positions))]
    #     return positions, colors, elements

    # def _read_lines_data(self) -> ShaderDataType:
    #     vertices = self.geometry._vertices
    #     positions = [vertices[vertex] for edge in self.geometry.edges for vertex in edge]
    #     colors = [self.linecolor] * 2 * len(positions)
    #     elements = [[2 * i, 2 * i + 1] for i in range(len(self.geometry.edges))]
    #     return positions, colors, elements

    # def _read_frontfaces_data(self) -> ShaderDataType:
    #     vertices = self.geometry._vertices
    #     positions = [vertices[vertex] for face in self.geometry.triangles for vertex in face]
    #     colors = [self.facecolor] * 3 * len(positions)
    #     elements = [[3 * i, 3 * i + 1, 3 * i + 2] for i in range(len(self.geometry.triangles))]
    #     return positions, colors, elements

    # def _read_backfaces_data(self) -> ShaderDataType:
    #     vertices = self.geometry._vertices
    #     positions = [vertices[vertex] for face in self.geometry.triangles for vertex in face]
    #     colors = [self.facecolor] * 3 * len(positions)
    #     elements = [[3 * i + 2, 3 * i + 1, 3 * i] for i in range(len(self.geometry.triangles))]
    #     return positions, colors, elements

    # def update_matrix(self):
    #     self._update_matrix()

    # def update(self, update_positions: bool = True, update_colors: bool = True, update_elements: bool = True):
    #     """Update the object.

    #     Parameters
    #     ----------
    #     update_positions : bool, optional
    #         Whether to update positions of the object.
    #     update_colors : bool, optional
    #         Whether to update colors of the object.
    #     update_elements : bool, optional
    #         Whether to update elements of the object.
    #     """

    #     # # Update the matrix from object's translation, rotation and scale.
    #     # self._update_matrix()

    #     # self._points_data = self._read_points_data()
    #     # self._lines_data = self._read_lines_data()
    #     # self._frontfaces_data = self._read_frontfaces_data()
    #     # self._backfaces_data = self._read_backfaces_data()

    #     # # Update all buffers from object's data.
    #     # if self._points_data is not None:
    #     #     self.update_buffer_from_data(
    #     #         self._points_data,
    #     #         self._points_buffer,
    #     #         update_positions,
    #     #         update_colors,
    #     #         update_elements,
    #     #     )
    #     # if self._lines_data is not None:
    #     #     self.update_buffer_from_data(
    #     #         self._lines_data,
    #     #         self._lines_buffer,
    #     #         update_positions,
    #     #         update_colors,
    #     #         update_elements,
    #     #     )
    #     # if self._frontfaces_data is not None:
    #     #     self.update_buffer_from_data(
    #     #         self._frontfaces_data,
    #     #         self._frontfaces_buffer,
    #     #         update_positions,
    #     #         update_colors,
    #     #         update_elements,
    #     #     )
    #     # if self._backfaces_data is not None:
    #     #     self.update_buffer_from_data(
    #     #         self._backfaces_data,
    #     #         self._backfaces_buffer,
    #     #         update_positions,
    #     #         update_colors,
    #     #         update_elements,
    #     #     )
