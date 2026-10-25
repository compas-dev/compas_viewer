from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy import array
from numpy import average
from numpy.typing import NDArray

from compas.colors import Color
from compas.data import Data
from compas.geometry import Point
from compas.geometry import transform_points_numpy
from compas.scene import SceneObject

from .parameters import ObjectParameter
from .parameters import inspect_object_parameters
from .parameters import object_parameter_values

# Type template of point/line/face data for generating the buffers.
type BufferValues = Sequence[Any] | NDArray[Any]
type ShaderDataType = tuple[BufferValues, BufferValues | None, BufferValues]


class ViewerSceneObject(SceneObject):
    """Base class for viewer scene objects with render-buffer support.

    Parameters
    ----------
    is_selected
        Whether the object is selected. Default is False.
    show
        Whether to show object. Default is True.
    show_points
        Whether to show points/vertices of the object. Default is the value of `show_points` in `viewer.config`.
    show_lines
        Whether to show lines/edges of the object. Default is the value of `show_lines` in `viewer.config`.
    show_faces
        Whether to show faces of the object. Default is the value of `show_faces` in `viewer.config`.
    linewidth
        The line width to be drawn on screen. Default is the value of `linewidth` in `viewer.config`.
    pointsize
        The point size to be drawn on screen. Default is the value of `pointsize` in `viewer.config`.
    opacity
        The opacity of the object. Default is the value of `opacity` in `viewer.config`.
    use_rgba
        Whether buffer colors contain alpha values.
    **kwargs
        Additional COMPAS scene-object options.

    """

    def __init__(
        self,
        is_selected: bool = False,
        show: bool = True,
        show_points: bool | None = None,
        show_lines: bool | None = None,
        show_faces: bool | None = None,
        linewidth: float | None = None,
        pointsize: float | None = None,
        opacity: float | None = None,
        use_rgba: bool = False,
        **kwargs: Any,
    ) -> None:
        #  Basic
        super().__init__(**kwargs)
        self.show = show
        self.show_points = show_points if show_points is not None else False
        self.show_lines = show_lines if show_lines is not None else True
        self.show_faces = show_faces if show_faces is not None else True
        self.linewidth = linewidth if linewidth is not None else self.viewer.config.display.linewidth
        self.pointsize = pointsize if pointsize is not None else self.viewer.config.display.pointsize
        self.opacity = opacity if opacity is not None else self.viewer.config.display.opacity

        #  Selection
        self.is_selected = is_selected

        #  Visual
        self.background: bool = False
        self.use_rgba = use_rgba

        #  Geometric
        self._bounding_box: list[list[float]] | None = None
        self._bounding_box_center: Point | None = None

        #  Primitive
        self._points_data: ShaderDataType | None = None
        self._lines_data: ShaderDataType | None = None
        self._frontfaces_data: ShaderDataType | None = None
        self._backfaces_data: ShaderDataType | None = None

        self._inited = False
        self.context = "Viewer"

    @property
    def viewer(self) -> Any:
        """Viewer: The shared viewer instance."""
        from compas_viewer.viewer import Viewer

        return Viewer()

    @property
    def bounding_box(self) -> list[list[float]] | None:
        """list[list[float]] | None: World-space minimum and maximum corners."""
        return self._bounding_box

    @property
    def bounding_box_center(self) -> Point | None:
        """Point | None: Center of the world-space bounding box."""
        return self._bounding_box_center

    @property
    def data(self) -> Data | None:
        """Data | None: Underlying COMPAS data or geometry object."""
        return self.item

    @property
    def parameters(self) -> dict[str, Any]:
        """dict[str, Any]: Recoverable constructor parameter values."""
        return object_parameter_values(self.data)

    @property
    def parameter_info(self) -> dict[str, ObjectParameter]:
        """dict[str, ObjectParameter]: Constructor parameter metadata."""
        return inspect_object_parameters(self.data)

    # ==========================================================================
    # Reading geometric data, downstream classes should implement these properties.
    # ==========================================================================

    def _read_points_data(self) -> ShaderDataType | None:
        """Read points data from the object."""
        pass

    def _read_lines_data(self) -> ShaderDataType | None:
        """Read lines data from the object."""
        pass

    def _read_frontfaces_data(self) -> ShaderDataType | None:
        """Read frontfaces data from the object."""
        pass

    def _read_backfaces_data(self) -> ShaderDataType | None:
        """Read backfaces data from the object."""
        pass

    # ==========================================================================
    # general
    # ==========================================================================

    def init(self) -> None:
        """Initialize render data, bounds, and instance-selection color."""
        self.refresh_data()
        self.instance_color = Color.from_rgb255(*next(self.viewer.scene._instance_colors_generator))
        self.viewer.scene.instance_colors[self.instance_color.rgb255] = self

    def refresh_data(self) -> None:
        """Regenerate render data and bounds from the underlying object."""
        self._points_data = self._read_points_data()
        self._lines_data = self._read_lines_data()
        self._frontfaces_data = self._read_frontfaces_data()
        self._backfaces_data = self._read_backfaces_data()
        self._update_bounding_box()

    def update(self, update_transform: bool = True, update_data: bool = False) -> None:
        """Update the object.

        Parameters
        ----------
        update_transform
            Whether to update the transform of the object.
        update_data
            Whether to update the geometric data of the object.

        """
        if update_transform:
            self.buffer_manager.update_object_transform(self)
        if update_data:
            self.buffer_manager.update_object_data(self)

    def _update_bounding_box(self, positions: BufferValues | None = None) -> None:
        """Update the bounding box of the object"""
        if positions is None:
            positions = np.array([]).reshape(0, 3)
            if self._points_data is not None and len(self._points_data[0]) > 0:
                positions = np.vstack([positions, self._points_data[0]])
            if self._lines_data is not None and len(self._lines_data[0]) > 0:
                positions = np.vstack([positions, self._lines_data[0]])
            if self._frontfaces_data is not None and len(self._frontfaces_data[0]) > 0:
                positions = np.vstack([positions, self._frontfaces_data[0]])
            if len(positions) == 0:
                return

        _positions = array(positions)
        self._bounding_box = list(transform_points_numpy(array([_positions.min(axis=0), _positions.max(axis=0)]), self.worldtransformation.matrix))
        center = average(a=array(self.bounding_box), axis=0)
        self._bounding_box_center = Point(center[0], center[1], center[2])

    @property
    def settings(self) -> dict[str, Any]:
        """dict[str, Any]: Current display settings for the scene object."""
        settings = {
            "name": self.name,
            "is_selected": self.is_selected,
            "show": self.show,
            "show_points": self.show_points,
            "show_lines": self.show_lines,
            "show_faces": self.show_faces,
            "linewidth": self.linewidth,
            "pointsize": self.pointsize,
            "opacity": self.opacity,
            "background": self.background,
        }

        if hasattr(self, "pointcolor"):
            settings["pointcolor"] = getattr(self, "pointcolor")

        if hasattr(self, "linecolor"):
            settings["linecolor"] = getattr(self, "linecolor")

        if hasattr(self, "facecolor"):
            settings["facecolor"] = getattr(self, "facecolor")

        return settings

    @property
    def buffer_manager(self) -> Any:
        """BufferManager: Renderer buffer manager used by this object."""
        return self.viewer.renderer.buffer_manager
