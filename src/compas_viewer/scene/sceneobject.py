from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy import array
from numpy import average
from numpy.typing import NDArray

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import transform_points_numpy
from compas.scene import SceneObject

from .parameters import ObjectParameter
from .parameters import inspect_object_parameters
from .parameters import object_parameter_values

# Type template of point/line/face data for generating the buffers.
type BufferValues = Sequence[Any] | NDArray[Any]
type ShaderDataType = tuple[BufferValues, BufferValues | None, BufferValues]


class ViewerSceneObject:
    """Transient Viewer render state for a stable COMPAS scene object.

    Parameters
    ----------
    is_selected
        Whether the object is selected. Default is False.
    show
        Whether to show object. Default is True.
    show_points
        Whether to show points or vertices of the object.
    show_lines
        Whether to show lines or edges of the object.
    show_faces
        Whether to show faces of the object.
    linewidth
        The line width to draw on screen.
    pointsize
        The point size to draw on screen.
    opacity
        The opacity of the object.
    use_rgba
        Whether buffer colors contain alpha values.
    **kwargs
        Additional COMPAS scene-object options.

    """

    def __init__(
        self,
        sceneobject: SceneObject,
        runtime: Any,
        **kwargs: Any,
    ) -> None:
        object.__setattr__(self, "sceneobject", sceneobject)
        object.__setattr__(self, "runtime", runtime)

        #  Visual
        #  Geometric
        self._bounding_box: list[list[float]] | None = None
        self._bounding_box_center: Point | None = None

        #  Primitive
        self._points_data: ShaderDataType | None = None
        self._lines_data: ShaderDataType | None = None
        self._frontfaces_data: ShaderDataType | None = None
        self._backfaces_data: ShaderDataType | None = None

        self._inited = False
        self._inited = False

    def __getattr__(self, name: str) -> Any:
        """Delegate durable presentation and item access to the stable object."""
        return getattr(self.sceneobject, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Store durable fields on the stable object and runtime fields locally."""
        sceneobject = self.__dict__.get("sceneobject")
        if sceneobject is not None and hasattr(sceneobject, name):
            setattr(sceneobject, name, value)
        else:
            object.__setattr__(self, name, value)

    @property
    def viewer(self) -> Any:
        """The Viewer instance that owns this transient render state."""
        from .scene import ViewerScene

        if isinstance(self.runtime, ViewerScene):
            return self.runtime.viewer
        if getattr(self.runtime, "scene", None) is self.runtime_scene:
            return self.runtime
        raise RuntimeError("This render helper is not attached to a Viewer runtime.")

    @property
    def runtime_scene(self) -> Any:
        """The ViewerScene that owns this transient render state."""
        return getattr(self.runtime, "scene", self.runtime)

    @property
    def is_selected(self) -> bool:
        """Whether the stable object is selected in the current Viewer."""
        return self.runtime_scene.is_selected(self.sceneobject)

    @is_selected.setter
    def is_selected(self, selected: bool) -> None:
        self.runtime_scene.set_selected(self.sceneobject, selected)

    @property
    def show_faces(self) -> bool:
        """Whether to display surface geometry as faces."""
        return self.show_surfaces

    @show_faces.setter
    def show_faces(self, show: bool) -> None:
        self.show_surfaces = show

    @property
    def parent(self) -> "ViewerSceneObject | None":
        """Transient render state of the stable parent, when rendered."""
        parent = self.sceneobject.parent
        return self.runtime_scene.render_objects.get(parent.guid) if parent is not None else None

    @property
    def bounding_box(self) -> list[list[float]] | None:
        """list[list[float]] | None: World-space minimum and maximum corners."""
        return self._bounding_box

    @property
    def bounding_box_center(self) -> Point | None:
        """Point | None: Center of the world-space bounding box."""
        return self._bounding_box_center

    @property
    def data(self) -> Any:
        """Underlying COMPAS data or geometry object."""
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
        previous = getattr(self, "instance_color", None)
        if previous is not None and self.runtime_scene.instance_colors.get(previous.rgb255) is self.sceneobject:
            self.runtime_scene.instance_colors.pop(previous.rgb255)
        self.instance_color = Color.from_rgb255(*next(self.runtime_scene._instance_colors_generator))
        self.runtime_scene.instance_colors[self.instance_color.rgb255] = self.sceneobject
        self._inited = True

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
    def buffer_manager(self) -> Any:
        """BufferManager: Renderer buffer manager used by this object."""
        return self.viewer.renderer.buffer_manager
