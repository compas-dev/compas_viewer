from collections.abc import Callable
from typing import Any
from uuid import UUID

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from compas.scene import SceneObject
from compas_viewer.config import Config
from compas_viewer.selection import Selection


def _unbound_sceneobject(_guid: UUID) -> SceneObject:
    raise RuntimeError("This ViewerState is not bound to a Viewer scene.")


class ViewerState(QObject):
    """Provide observable access to the viewer's runtime configuration state.

    Parameters
    ----------
    config
        Persistent configuration used as the backing store.
    resolve_sceneobject
        Resolve stable object GUIDs in the current Viewer scene. Direct state
        construction may omit the resolver when selection is unused.

    """

    changed = Signal(str, object)

    def __init__(
        self,
        config: Config,
        resolve_sceneobject: Callable[[UUID], SceneObject] | None = None,
    ) -> None:
        super().__init__()
        self.config = config
        self.selection = Selection(resolve_sceneobject or _unbound_sceneobject, self._selection_changed)

    def get(self, path: str) -> Any:
        """Return a state value by dotted configuration path.

        Parameters
        ----------
        path
            Dotted path such as ``"renderer.show_grid"``.

        Returns
        -------
        Any
            Current value at the requested path.

        """
        target: Any = self.config
        for name in self._parts(path):
            target = getattr(target, name)
        return target

    def set(self, path: str, value: Any) -> bool:
        """Set and publish a state value when it changes.

        Parameters
        ----------
        path
            Dotted configuration path.
        value
            New state value.

        Returns
        -------
        bool
            Whether the stored value changed.

        """
        parts = self._parts(path)
        target: Any = self.config
        for name in parts[:-1]:
            target = getattr(target, name)
        name = parts[-1]
        if getattr(target, name) == value:
            return False
        setattr(target, name, value)
        self.changed.emit(path, value)
        return True

    def toggle(self, path: str) -> bool:
        """Invert and publish a boolean state value.

        Parameters
        ----------
        path
            Dotted path to a boolean value.

        Returns
        -------
        bool
            New boolean value.

        Raises
        ------
        TypeError
            If the current value is not a boolean.

        """
        value = self.get(path)
        if not isinstance(value, bool):
            raise TypeError(f"State value {path!r} is not boolean.")
        value = not value
        self.set(path, value)
        return value

    def notify(self, path: str) -> None:
        """Publish the current value after an external in-place assignment.

        Parameters
        ----------
        path
            Dotted configuration path to publish.

        """
        self.changed.emit(path, self.get(path))

    def _selection_changed(self, guids: tuple[UUID, ...]) -> None:
        """Bridge one Qt-neutral selection mutation to Viewer observers."""
        self.changed.emit("selection", guids)

    @staticmethod
    def _parts(path: str) -> list[str]:
        parts = path.split(".")
        if not path or any(not part for part in parts):
            raise ValueError(f"Invalid state path: {path!r}.")
        return parts


__all__ = ["ViewerState"]
