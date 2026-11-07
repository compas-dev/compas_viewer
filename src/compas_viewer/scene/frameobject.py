from typing import cast

from compas.colors import Color
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Transformation
from compas.scene import SceneStateField

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class FrameObject(ViewerSceneObject):
    """Viewer scene object for displaying a COMPAS frame.

    Parameters
    ----------
    size
        Length of each displayed frame axis. Use `None` to derive the size
        from the viewer configuration.
    **kwargs
        Additional scene-object options.

    See Also
    --------
    `compas.geometry.Frame`

    """

    __scene_state_namespace__ = "compas_viewer.scene.FrameObject"
    __scene_state_fields__ = (SceneStateField("size", (int, float, type(None))),)

    def __init__(self, size: float | None = 1, **kwargs) -> None:
        super().__init__(**kwargs)
        self.size = size

    def _read_lines_data(self) -> ShaderDataType:
        trans = Transformation.from_frame_to_frame(Frame.worldXY(), cast(Frame, self.item))
        size = cast(float, self.size)

        positions = []
        colors = []
        elements = []

        # X direction
        colors.append(Color.red())
        colors.append(Color.red())
        positions.append(Point(0, 0, 0).transformed(trans))
        positions.append(Point(size, 0, 0).transformed(trans))
        elements.append([0, 1])

        # Y direction
        colors.append(Color.green())
        colors.append(Color.green())
        positions.append(Point(0, 0, 0).transformed(trans))
        positions.append(Point(0, size, 0).transformed(trans))
        elements.append([2, 3])

        # Z direction
        colors.append(Color.blue())
        colors.append(Color.blue())
        positions.append(Point(0, 0, 0).transformed(trans))
        positions.append(Point(0, 0, size).transformed(trans))
        elements.append([4, 5])

        return positions, colors, elements
