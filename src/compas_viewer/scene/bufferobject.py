from typing import Any
from typing import cast

import numpy as np
from numpy.typing import NDArray

from compas.geometry import Geometry
from compas_viewer.scene import ViewerSceneObject

from .sceneobject import ShaderDataType


class BufferGeometry(Geometry):
    """A geometry defined directly from the buffer data.

    Parameters
    ----------
    points
        The flat list of point locations, in the form of [x1, y1, z1, x2, y2, z2, ...].
    lines
        The flat list of line segment vertices, in the form of [x1, y1, z1, x2, y2, z2, ...].
    faces
        The flat list of face vertices, in the form of [x1, y1, z1, x2, y2, z2, ...].
    pointcolor
        The flat list of point colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].
    linecolor
        The flat list of line vertices colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].
    facecolor
        The flat list of face vertices colors, in the form of [r1, g1, b1, a1, r2, g2, b2, a2, ...].

    """

    def __init__(
        self,
        points: NDArray | None = None,
        lines: NDArray | None = None,
        faces: NDArray | None = None,
        pointcolor: NDArray | None = None,
        linecolor: NDArray | None = None,
        facecolor: NDArray | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.points = points
        self.lines = lines
        self.faces = faces
        self.pointcolor = pointcolor
        self.linecolor = linecolor
        self.facecolor = facecolor


class BufferObject(ViewerSceneObject):
    """Display geometry supplied directly as render-buffer arrays.

    Parameters
    ----------
    show_points
        Whether to show the points or not.
    show_lines
        Whether to show the lines or not.
    show_faces
        Whether to show the faces or not.
    **kwargs
        Additional keyword arguments.

    """

    def __init__(self, *args: Any, show_points: bool = True, show_lines: bool = True, show_faces: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.show_points = show_points if show_points is not None else self.buffergeometry.points is not None
        self.show_lines = show_lines if show_lines is not None else self.buffergeometry.lines is not None
        self.show_faces = show_faces if show_faces is not None else self.buffergeometry.faces is not None

    @property
    def buffergeometry(self) -> BufferGeometry:
        return cast(BufferGeometry, self.item)

    def _get_num_vertices(self, positions: NDArray) -> int:
        """Get the number of vertices from positions array.

        Handles both flat 1D arrays [x1, y1, z1, x2, y2, z2, ...] and
        2D arrays with shape (N, 3).
        """
        if positions.ndim == 1:
            return positions.shape[0] // 3
        else:
            return positions.shape[0]

    def _read_points_data(self) -> ShaderDataType | None:
        """Read points data from the object."""
        if self.buffergeometry.points is None:
            return None
        positions = self.buffergeometry.points
        colors = self.buffergeometry.pointcolor
        elements = np.arange(self._get_num_vertices(positions), dtype=int)
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType | None:
        """Read lines data from the object."""
        if self.buffergeometry.lines is None:
            return None
        positions = self.buffergeometry.lines
        colors = self.buffergeometry.linecolor
        elements = np.arange(self._get_num_vertices(positions), dtype=int)
        return positions, colors, elements

    def _read_frontfaces_data(self) -> ShaderDataType | None:
        """Read frontfaces data from the object."""
        if self.buffergeometry.faces is None:
            return None
        positions = self.buffergeometry.faces
        colors = self.buffergeometry.facecolor
        elements = np.arange(self._get_num_vertices(positions), dtype=int)
        return positions, colors, elements

    def _read_backfaces_data(self) -> ShaderDataType | None:
        """Read backfaces data from the object."""
        if self.buffergeometry.faces is None:
            return None
        positions = self.buffergeometry.faces
        colors = self.buffergeometry.facecolor
        elements = np.flip(np.arange(self._get_num_vertices(positions), dtype=int))
        return positions, colors, elements
