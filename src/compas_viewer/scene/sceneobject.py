from typing import Optional

import numpy as np
from numpy import array
from numpy import average

from compas.colors import Color
from compas.geometry import Point
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
        # Initialize private attributes BEFORE super().__init__() because
        # base classes may set properties that trigger our setters
        self._inited = False
        self._show = show
        self._show_points = show_points if show_points is not None else False
        self._show_lines = show_lines if show_lines is not None else True
        self._show_faces = show_faces if show_faces is not None else True
        self._linewidth = linewidth
        self._pointsize = pointsize
        self._opacity = opacity
        self._is_selected = is_selected

        super().__init__(**kwargs)

        # Apply defaults after super().__init__() when self.viewer is available
        if self._linewidth is None:
            self._linewidth = self.viewer.config.ui.display.linewidth
        if self._pointsize is None:
            self._pointsize = self.viewer.config.ui.display.pointsize
        if self._opacity is None:
            self._opacity = self.viewer.config.ui.display.opacity

        #  Visual
        self.background: bool = False
        self.use_rgba = use_rgba

        #  Geometric
        self._bounding_box: Optional[list[float]] = None
        self._bounding_box_center: Optional[Point] = None

        #  Primitive
        self._points_data: Optional[ShaderDataType] = None
        self._lines_data: Optional[ShaderDataType] = None
        self._frontfaces_data: Optional[ShaderDataType] = None
        self._backfaces_data: Optional[ShaderDataType] = None

        self.context = "Viewer"

    def _mark_settings_dirty(self):
        """Mark this object's settings as needing GPU update."""
        if self._inited:
            self.buffer_manager.mark_settings_dirty(self)

    @property
    def show(self) -> bool:
        return self._show

    @show.setter
    def show(self, value: bool):
        if self._show != value:
            self._show = value
            self._mark_settings_dirty()

    @property
    def show_points(self) -> bool:
        return self._show_points

    @show_points.setter
    def show_points(self, value: bool):
        if self._show_points != value:
            self._show_points = value
            self._mark_settings_dirty()

    @property
    def show_lines(self) -> bool:
        return self._show_lines

    @show_lines.setter
    def show_lines(self, value: bool):
        if self._show_lines != value:
            self._show_lines = value
            self._mark_settings_dirty()

    @property
    def show_faces(self) -> bool:
        return self._show_faces

    @show_faces.setter
    def show_faces(self, value: bool):
        if self._show_faces != value:
            self._show_faces = value
            self._mark_settings_dirty()

    @property
    def linewidth(self) -> float:
        return self._linewidth

    @linewidth.setter
    def linewidth(self, value: float):
        if self._linewidth != value:
            self._linewidth = value
            self._mark_settings_dirty()

    @property
    def pointsize(self) -> float:
        return self._pointsize

    @pointsize.setter
    def pointsize(self, value: float):
        if self._pointsize != value:
            self._pointsize = value
            self._mark_settings_dirty()

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        if self._opacity != value:
            self._opacity = value
            self._mark_settings_dirty()

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        if self._is_selected != value:
            self._is_selected = value
            self._mark_settings_dirty()

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
        pass

    def _read_lines_data(self) -> Optional[ShaderDataType]:
        """Read lines data from the object."""
        pass

    def _read_frontfaces_data(self) -> Optional[ShaderDataType]:
        """Read frontfaces data from the object."""
        pass

    def _read_backfaces_data(self) -> Optional[ShaderDataType]:
        """Read backfaces data from the object."""
        pass

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
        self._inited = True

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
            if self._points_data is not None and len(self._points_data[0]) > 0:
                positions = np.vstack([positions, self._points_data[0]])
            if self._lines_data is not None and len(self._lines_data[0]) > 0:
                positions = np.vstack([positions, self._lines_data[0]])
            if self._frontfaces_data is not None and len(self._frontfaces_data[0]) > 0:
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
