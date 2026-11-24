from collections.abc import Sequence
from typing import Any
from typing import Self
from typing import cast

import numpy as np
from numpy.typing import NDArray

from compas.geometry import Geometry

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class BufferGeometry(Geometry):
    """Shared vertices and indexed primitives ready for Viewer buffers.

    Parameters
    ----------
    vertices
        Vertex coordinates with shape ``(N, 3)``.
    points
        Optional point indices with shape ``(P,)``.
    edges
        Optional edge indices with shape ``(E, 2)``.
    triangles
        Optional triangle indices with shape ``(T, 3)``.
    pointcolor
        Optional vertex colors for points with shape ``(N, 4)``.
    linecolor
        Optional vertex colors for edges with shape ``(N, 4)``.
    facecolor
        Optional vertex colors for triangles with shape ``(N, 4)``.

    Notes
    -----
    Inputs are copied into contiguous ``float32`` vertex/color arrays and
    ``int32`` index arrays. Colors remain vertex-indexed; per-edge and
    per-triangle colors are not supported.

    """

    def __init__(
        self,
        vertices: Sequence[Sequence[float]] | NDArray[Any],
        points: Sequence[int] | NDArray[Any] | None = None,
        edges: Sequence[Sequence[int]] | NDArray[Any] | None = None,
        triangles: Sequence[Sequence[int]] | NDArray[Any] | None = None,
        pointcolor: Sequence[Sequence[float]] | NDArray[Any] | None = None,
        linecolor: Sequence[Sequence[float]] | NDArray[Any] | None = None,
        facecolor: Sequence[Sequence[float]] | NDArray[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.vertices = self._normalize_vertices(vertices)
        self.points = self._normalize_indices(points, width=None, name="points")
        self.edges = self._normalize_indices(edges, width=2, name="edges")
        self.triangles = self._normalize_indices(triangles, width=3, name="triangles")
        self._validate_index_bounds()
        self.pointcolor = self._normalize_colors(pointcolor, "pointcolor", active=self.points is not None)
        self.linecolor = self._normalize_colors(linecolor, "linecolor", active=self.edges is not None)
        self.facecolor = self._normalize_colors(facecolor, "facecolor", active=self.triangles is not None)

    @property
    def __data__(self) -> dict[str, list[Any] | None]:
        """dict[str, list[Any] | None]: Serializable indexed-buffer data."""
        return {
            "vertices": self.vertices.tolist(),
            "points": None if self.points is None else self.points.tolist(),
            "edges": None if self.edges is None else self.edges.tolist(),
            "triangles": None if self.triangles is None else self.triangles.tolist(),
            "pointcolor": None if self.pointcolor is None else self.pointcolor.tolist(),
            "linecolor": None if self.linecolor is None else self.linecolor.tolist(),
            "facecolor": None if self.facecolor is None else self.facecolor.tolist(),
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        """Construct indexed buffer geometry from its closed data schema."""
        fields = {"vertices", "points", "edges", "triangles", "pointcolor", "linecolor", "facecolor"}
        unknown = set(data) - fields
        missing = fields - set(data)
        if unknown:
            raise ValueError(f"Unknown buffer-geometry fields: {sorted(unknown)}")
        if missing:
            raise ValueError(f"Missing buffer-geometry fields: {sorted(missing)}")
        return cls(**data)

    @classmethod
    def from_points(cls, vertices: Sequence[Sequence[float]] | NDArray[Any], **kwargs: Any) -> Self:
        """Construct point geometry using every vertex once.

        Parameters
        ----------
        vertices
            Vertex coordinates with shape ``(N, 3)``.
        **kwargs
            Optional vertex colors and COMPAS data arguments.

        Returns
        -------
        Self

        """
        vertex_array = cls._normalize_vertices(vertices)
        return cls(vertex_array, points=np.arange(len(vertex_array), dtype=np.int32), **kwargs)

    @classmethod
    def from_vertices_and_edges(
        cls,
        vertices: Sequence[Sequence[float]] | NDArray[Any],
        edges: Sequence[Sequence[int]] | NDArray[Any],
        **kwargs: Any,
    ) -> Self:
        """Construct indexed line geometry.

        Parameters
        ----------
        vertices
            Vertex coordinates with shape ``(N, 3)``.
        edges
            Edge indices with shape ``(E, 2)``.
        **kwargs
            Optional vertex colors and COMPAS data arguments.

        Returns
        -------
        Self

        """
        return cls(vertices, edges=edges, **kwargs)

    @classmethod
    def from_vertices_and_triangles(
        cls,
        vertices: Sequence[Sequence[float]] | NDArray[Any],
        triangles: Sequence[Sequence[int]] | NDArray[Any],
        **kwargs: Any,
    ) -> Self:
        """Construct indexed triangle geometry.

        Parameters
        ----------
        vertices
            Vertex coordinates with shape ``(N, 3)``.
        triangles
            Triangle indices with shape ``(T, 3)``.
        **kwargs
            Optional vertex colors and COMPAS data arguments.

        Returns
        -------
        Self

        """
        return cls(vertices, triangles=triangles, **kwargs)

    @staticmethod
    def _normalize_vertices(values: Sequence[Sequence[float]] | NDArray[Any]) -> NDArray[np.float32]:
        array = np.asarray(values, dtype=np.float32)
        if array.size == 0:
            array = array.reshape((0, 3))
        if array.ndim != 2 or array.shape[1] != 3:
            raise ValueError("Vertices should have shape (N, 3).")
        return np.array(array, dtype=np.float32, order="C", copy=True)

    @staticmethod
    def _normalize_indices(values: Sequence[Any] | NDArray[Any] | None, width: int | None, name: str) -> NDArray[np.int32] | None:
        if values is None:
            return None
        source = np.asarray(values)
        if source.dtype.kind == "f":
            if not np.isfinite(source).all() or not np.equal(source, np.trunc(source)).all():
                raise ValueError(f"{name.capitalize()} should contain integral vertex indices.")
        elif source.dtype.kind not in "biu":
            raise ValueError(f"{name.capitalize()} should contain integral vertex indices.")
        if source.size and (source.min() < np.iinfo(np.int32).min or source.max() > np.iinfo(np.int32).max):
            raise ValueError(f"{name.capitalize()} contain an index outside the int32 range.")
        array = np.asarray(source, dtype=np.int32)
        if array.size == 0:
            array = array.reshape((0,) if width is None else (0, width))
        expected = f"(N, {width})" if width is not None else "(N,)"
        if width is None and array.ndim != 1:
            raise ValueError(f"{name.capitalize()} should have shape {expected}.")
        if width is not None and (array.ndim != 2 or array.shape[1] != width):
            raise ValueError(f"{name.capitalize()} should have shape {expected}.")
        return np.array(array, dtype=np.int32, order="C", copy=True)

    def _normalize_colors(
        self,
        values: Sequence[Sequence[float]] | NDArray[Any] | None,
        name: str,
        active: bool,
    ) -> NDArray[np.float32] | None:
        if values is None:
            return np.ones((len(self.vertices), 4), dtype=np.float32) if active else None
        array = np.asarray(values, dtype=np.float32)
        if array.size == 0 and len(self.vertices) == 0:
            array = array.reshape((0, 4))
        if array.ndim != 2 or array.shape != (len(self.vertices), 4):
            raise ValueError(f"{name.capitalize()} should have shape (N, 4), with one color per vertex.")
        return np.array(array, dtype=np.float32, order="C", copy=True)

    def _validate_index_bounds(self) -> None:
        for name, indices in (("points", self.points), ("edges", self.edges), ("triangles", self.triangles)):
            if indices is None or indices.size == 0:
                continue
            if indices.min() < 0 or indices.max() >= len(self.vertices):
                raise ValueError(f"{name.capitalize()} contain a vertex index outside [0, {len(self.vertices)}).")


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

    @property
    def buffergeometry(self) -> BufferGeometry:
        """BufferGeometry: The typed indexed geometry."""
        return cast(BufferGeometry, self.item)

    def _read_points_data(self) -> ShaderDataType | None:
        """Read points data from the object."""
        if self.buffergeometry.points is None:
            return None
        assert self.buffergeometry.pointcolor is not None
        return self.buffergeometry.vertices, self.buffergeometry.pointcolor, self.buffergeometry.points

    def _read_lines_data(self) -> ShaderDataType | None:
        """Read lines data from the object."""
        if self.buffergeometry.edges is None:
            return None
        assert self.buffergeometry.linecolor is not None
        return self.buffergeometry.vertices, self.buffergeometry.linecolor, self.buffergeometry.edges

    def _read_frontfaces_data(self) -> ShaderDataType | None:
        """Read frontfaces data from the object."""
        if self.buffergeometry.triangles is None:
            return None
        assert self.buffergeometry.facecolor is not None
        return self.buffergeometry.vertices, self.buffergeometry.facecolor, self.buffergeometry.triangles

    def _read_backfaces_data(self) -> ShaderDataType | None:
        """Read backfaces data from the object."""
        if self.buffergeometry.triangles is None:
            return None
        assert self.buffergeometry.facecolor is not None
        elements = self.buffergeometry.triangles[:, [0, 2, 1]]
        return self.buffergeometry.vertices, self.buffergeometry.facecolor, elements
