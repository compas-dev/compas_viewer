from compas.geometry import Point
from compas.geometry import Pointcloud
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PointcloudObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Pointcloud geometry.

    Parameters
    ----------
    pointcloud : :class:`compas.geometry.PointCloud`
        The point cloud geometry to display.
    show_points : bool, optional
        Whether to display the point in the viewer. Default is True.

    See Also
    --------
    :class:`compas.geometry.Pointcloud`
    """

    def __init__(self, pointcloud: Pointcloud, **kwargs):
        super().__init__(geometry=pointcloud, **kwargs)
        self.show_points = True
        self.geometry: Pointcloud

    @property
    def points(self) -> list[Point]:
        """The points to be shown in the viewer."""
        return self.geometry.points

    @property
    def lines(self) -> None:
        """The lines to be shown in the viewer."""
        return None

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        return None
