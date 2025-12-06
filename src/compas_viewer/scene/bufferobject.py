from typing import Optional

import numpy as np
from numpy.typing import NDArray

from compas.geometry import Geometry
from compas_viewer.scene import ViewerSceneObject


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


class BufferObject(ViewerSceneObject):
    """The SceneObject for the BufferGeometry.

    Parameters
    ----------
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

    def __init__(self, *args, show_points: bool = True, show_lines: bool = True, show_faces: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_points = show_points if show_points is not None else self.buffergeometry.points is not None
        self.show_lines = show_lines if show_lines is not None else self.buffergeometry.lines is not None
        self.show_faces = show_faces if show_faces is not None else self.buffergeometry.faces is not None

    @property
    def buffergeometry(self) -> BufferGeometry:
        return self.item

    def _get_num_vertices(self, positions: NDArray) -> int:
        """Get the number of vertices from positions array.

        Handles both flat 1D arrays [x1, y1, z1, x2, y2, z2, ...] and
        2D arrays with shape (N, 3).
        """
        if positions.ndim == 1:
            return positions.shape[0] // 3
        else:
            return positions.shape[0]

    def _read_points_data(self):
        """Read points data from the object."""
        if self.buffergeometry.points is None:
            return None
        positions = self.buffergeometry.points
        colors = self.buffergeometry.pointcolor
        elements = np.arange(self._get_num_vertices(positions), dtype=int)
        return positions, colors, elements

    def _read_lines_data(self):
        """Read lines data from the object."""
        if self.buffergeometry.lines is None:
            return None
        positions = self.buffergeometry.lines
        colors = self.buffergeometry.linecolor
        elements = np.arange(self._get_num_vertices(positions), dtype=int)
        return positions, colors, elements

    def _read_frontfaces_data(self):
        """Read frontfaces data from the object."""
        if self.buffergeometry.faces is None:
            return None
        positions = self.buffergeometry.faces
        colors = self.buffergeometry.facecolor
        elements = np.arange(self._get_num_vertices(positions), dtype=int)
        return positions, colors, elements

    def _read_backfaces_data(self):
        """Read backfaces data from the object."""
        if self.buffergeometry.faces is None:
            return None
        positions = self.buffergeometry.faces
        colors = self.buffergeometry.facecolor
        elements = np.flip(np.arange(self._get_num_vertices(positions), dtype=int))
        return positions, colors, elements
