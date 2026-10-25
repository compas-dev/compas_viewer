from abc import abstractmethod

from compas.geometry import Tessellation

from .geometryobject import GeometryObject
from .sceneobject import ShaderDataType


class TessellationObject(GeometryObject):
    """Base scene object for geometry with an indexed tessellation."""

    @property
    @abstractmethod
    def tessellation(self) -> Tessellation:
        """The render-ready tessellation of the geometry."""

    def _read_frontfaces_data(self) -> ShaderDataType:
        tessellation = self.tessellation
        positions = tessellation.vertices
        colors = [self.facecolor] * tessellation.number_of_vertices
        elements = [list(triangle) for triangle in tessellation.triangles]
        return positions, colors, elements

    def _read_backfaces_data(self) -> ShaderDataType:
        tessellation = self.tessellation
        positions = tessellation.vertices
        colors = [self.facecolor] * tessellation.number_of_vertices
        elements = [list(reversed(triangle)) for triangle in tessellation.triangles]
        return positions, colors, elements
