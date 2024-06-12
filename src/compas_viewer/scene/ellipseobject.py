from typing import Optional

from compas.geometry import Ellipse
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class EllipseObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Ellipse geometry.

    Parameters
    ----------
    ellipse : :class:`compas.geometry.Ellipse`
        A COMPAS ellipse geometry.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`
        and :class:`compas.scene.GeometryObject`.

    See Also
    --------
    :class:`compas.geometry.Ellipse`
    """

    def __init__(self, ellipse: Ellipse, **kwargs):
        super().__init__(geometry=ellipse, **kwargs)
        self.geometry: Ellipse
        self.show_lines = True

    @property
    def points(self) -> Optional[list[Point]]:
        return [self.geometry.plane.point]

    @property
    def lines(self) -> Optional[list[Line]]:
        return self.geometry.to_polyline(n=self.u).lines

    @property
    def viewmesh(self):
        return None
