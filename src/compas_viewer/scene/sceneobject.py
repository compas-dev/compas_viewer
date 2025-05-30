from typing import Any
from typing import Optional

import numpy as np
from numpy import array
from numpy import average

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import transform_points_numpy
from compas.scene import SceneObject
from compas_viewer.base import Base

# Type template of point/line/face data for generating the buffers.
ShaderDataType = tuple[list[Point], list[Color], list[list[int]]]


class ViewerSceneObject(SceneObject, Base):
    """
    Base class for all Viewer scene objects
    which also includes the  GL buffer creation and drawing methods.

    Parameters
    ----------
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer object.
    is_selected : bool, optional
        Whether the object is selected. Default is False.
    show : bool, optional
        Whether to show object. Default is True.
    show_points : bool, optional
        Whether to show points/vertices of the object. Default is the value of `show_points` in `viewer.config`.
    show_lines : bool, optional
        Whether to show lines/edges of the object. Default is the value of `show_lines` in `viewer.config`.
    show_faces : bool, optional
        Whether to show faces of the object. Default is the value of `show_faces` in `viewer.config`.
    linewidth : float, optional
        The line width to be drawn on screen. Default is the value of `linewidth` in `viewer.config`.
    pointsize : float, optional
        The point size to be drawn on screen. Default is the value of `pointsize` in `viewer.config`.
    opacity : float, optional
        The opacity of the object. Default is the value of `opacity` in `viewer.config`.
    **kwargs : dict, optional
        Additional visualization options for :class:`compas.scene.SceneObject`.

    Attributes
    ----------
    is_selected : bool
        Whether the object is selected.
    show : bool
        Whether to show object.
    show_points : bool
        Whether to show points/vertices of the object.
    show_lines : bool
        Whether to show lines/edges of the object.
    show_faces : bool
        Whether to show faces of the object.
    linewidth : float
        The line width to be drawn on screen
    pointsize : float
        The point size to be drawn on screen.
    opacity : float
        The opacity of the object.
    background : bool
        Whether the object is drawn on the background with depth test disabled.
    bounding_box : list[float], read-only
        The min and max corners of object bounding box, as a numpy array of shape (2, 3).
    bounding_box_center : :class:`compas.geometry.Point`, read-only
        The center of object bounding box, as a point.

    See Also
    --------
    :class:`compas.scene.SceneObject`
    """

    def __init__(
        self,
        is_selected: bool = False,
        show: bool = True,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        show_faces: Optional[bool] = None,
        linewidth: Optional[float] = None,
        pointsize: Optional[float] = None,
        opacity: Optional[float] = None,
        use_rgba: bool = False,
        **kwargs,
    ):
        #  Basic
        super().__init__(**kwargs)
        self.show = show
        self.show_points = show_points if show_points is not None else False
        self.show_lines = show_lines if show_lines is not None else True
        self.show_faces = show_faces if show_faces is not None else True
        self.linewidth = linewidth if linewidth is not None else self.viewer.config.ui.display.linewidth
        self.pointsize = pointsize if pointsize is not None else self.viewer.config.ui.display.pointsize
        self.opacity = opacity if opacity is not None else self.viewer.config.ui.display.opacity

        #  Selection
        self.is_selected = is_selected

        #  Visual
        self.background: bool = False
        self.use_rgba = use_rgba

        #  Geometric
        self.transformation: Optional[Transformation] = None
        self._bounding_box: Optional[list[float]] = None
        self._bounding_box_center: Optional[Point] = None

        #  Primitive
        self._points_data: Optional[ShaderDataType] = None
        self._lines_data: Optional[ShaderDataType] = None
        self._frontfaces_data: Optional[ShaderDataType] = None
        self._backfaces_data: Optional[ShaderDataType] = None
        self._points_buffer: [dict[str, Any]] = None  # type: ignore
        self._lines_buffer: [dict[str, Any]] = None  # type: ignore
        self._frontfaces_buffer: [dict[str, Any]] = None  # type: ignore
        self._backfaces_buffer: [dict[str, Any]] = None  # type: ignore

        self._inited = False

    @property
    def bounding_box(self):
        return self._bounding_box

    @property
    def bounding_box_center(self):
        return self._bounding_box_center

    # ==========================================================================
    # Reading geometric data, downstream classes should implement these properties.
    # ==========================================================================

    def _read_points_data(self) -> Optional[ShaderDataType]:
        """Read points data from the object."""
        raise NotImplementedError

    def _read_lines_data(self) -> Optional[ShaderDataType]:
        """Read lines data from the object."""
        raise NotImplementedError

    def _read_frontfaces_data(self) -> Optional[ShaderDataType]:
        """Read frontfaces data from the object."""
        raise NotImplementedError

    def _read_backfaces_data(self) -> Optional[ShaderDataType]:
        """Read backfaces data from the object."""
        raise NotImplementedError

    # ==========================================================================
    # general
    # ==========================================================================

    def init(self):
        """Initialize the object"""
        self._points_data = self._read_points_data()
        self._lines_data = self._read_lines_data()
        self._frontfaces_data = self._read_frontfaces_data()
        self._backfaces_data = self._read_backfaces_data()
        self._update_bounding_box()
        self.instance_color = Color.from_rgb255(*next(self.viewer.scene._instance_colors_generator))
        self.viewer.scene.instance_colors[self.instance_color.rgb255] = self

    def update(self, update_transform: bool = True, update_data: bool = False):
        """Update the object.

        Parameters
        ----------
        update_transform : bool, optional
            Whether to update the transform of the object.
        update_data : bool, optional
            Whether to update the geometric data of the object.
        """
        if update_transform:
            self.buffer_manager.update_object_transform(self)
        if update_data:
            self.buffer_manager.update_object_data(self)

    def _update_bounding_box(self, positions: Optional[list[Point]] = None):
        """Update the bounding box of the object"""
        if positions is None:
            positions = np.array([]).reshape(0, 3)
            if self._points_data is not None:
                positions = np.vstack([positions, self._points_data[0]])
            if self._lines_data is not None:
                positions = np.vstack([positions, self._lines_data[0]])
            if self._frontfaces_data is not None:
                positions = np.vstack([positions, self._frontfaces_data[0]])
            if len(positions) == 0:
                return

        _positions = array(positions)
        self._bounding_box = list(transform_points_numpy(array([_positions.min(axis=0), _positions.max(axis=0)]), self.worldtransformation))
        self._bounding_box_center = Point(*list(average(a=array(self.bounding_box), axis=0)))

    @property
    def settings(self):
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
            settings["pointcolor"] = self.pointcolor

        if hasattr(self, "linecolor"):
            settings["linecolor"] = self.linecolor

        if hasattr(self, "facecolor"):
            settings["facecolor"] = self.facecolor

        return settings

    @property
    def buffer_manager(self):
        return self.viewer.renderer.buffer_manager
