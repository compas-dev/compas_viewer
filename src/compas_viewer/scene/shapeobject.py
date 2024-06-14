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

    GEOMETRYBUFFER = {}

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
            
            # NOTE: this is not needed if vertices are not computed each time
            geometry = self.GEOMETRYBUFFER.get(id(self.geometry))
            if geometry is None:
                vertices = self.geometry.vertices
                edges = self.geometry.edges
                faces = self.geometry.triangles
                self.GEOMETRYBUFFER[id(self.geometry)] = (vertices, edges, faces)
            else:
                vertices, edges, faces = geometry

            pointcolor = [self.pointcolor.rgba] * len(vertices)
            linecolor = [self.linecolor.rgba] * len(edges) * 2
            facecolor = [self.facecolor.rgba] * len(faces) * 3
            self._buffergeometry = BufferGeometry(points=vertices, lineindices=edges, faceindices=faces, pointcolor=pointcolor, linecolor=linecolor, facecolor=facecolor)

        return self._buffergeometry
