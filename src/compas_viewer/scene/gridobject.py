from typing import Optional

from compas.colors import Color
from compas.geometry import Frame

from .frameobject import FrameObject


class GridObject(FrameObject):
    """
    The scene object of the world XY grid. It is a subclass of the FrameObject.

    Parameters
    ----------
    frame : :class:`compas.geometry.Frame`
        The transformation frame. The default is the world XY frame.
    framesize : tuple[float, int, float, int]
        The size of the grid in [dx, nx, dy, ny] format.
        Notice that the `nx` and `ny` must be even numbers.
    linecolor : :class:`compas.colors.Color`
        The color of the grid lines.
    show_framez : bool
        If True, the Z axis of the grid will be shown.

    Attributes
    ----------
    frame : :class:`compas.geometry.Frame`
        The transformation frame.
    dx : float
        The size of the grid in the X direction.
    nx : int
        The number of grid cells in the X direction.
    dy : float
        The size of the grid in the Y direction.
    ny : int
        The number of grid cells in the Y direction.
    show_framez : bool
        If the Z axis of the grid is shown.

    Notes
    -----
    The world grid object is always unselectable.

    See Also
    --------
    :class:`compas_viewer.scene.FrameObject`
    :class:`compas.geometry.Frame`
    """

    def __init__(
        self,
        frame: Frame = Frame.worldXY(),
        framesize: Optional[tuple[float, int, float, int]] = None,
        linecolor: Optional[Color] = None,
        show_framez: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(frame=frame, framesize=framesize, linecolor=linecolor, show_framez=show_framez, **kwargs)
        self.is_locked = True
