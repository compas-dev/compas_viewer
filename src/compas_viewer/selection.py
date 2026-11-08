from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from uuid import UUID

from compas.scene import SceneObject


class Selection:
    """Store one ordered Viewer selection independently of Qt and scene data.

    Parameters
    ----------
    resolve
        Resolve a stable scene-object GUID in the current Viewer scene.
    changed
        Callback invoked once with the complete ordered GUID tuple after each
        effective mutation.

    Notes
    -----
    Selection is transient Viewer state. It is not part of scene or Viewer
    configuration serialization.

    """

    def __init__(
        self,
        resolve: Callable[[UUID], SceneObject],
        changed: Callable[[tuple[UUID, ...]], None] | None = None,
    ) -> None:
        self._resolve = resolve
        self._changed = changed
        self._guids: dict[UUID, None] = {}

    def __bool__(self) -> bool:
        """Return whether at least one scene object is selected."""
        return bool(self._guids)

    def __contains__(self, sceneobject: SceneObject | UUID) -> bool:
        """Return whether a scene object or GUID is selected."""
        guid = sceneobject if isinstance(sceneobject, UUID) else sceneobject.guid
        return guid in self._guids

    def __iter__(self) -> Iterator[SceneObject]:
        """Iterate over selected scene objects in selection order."""
        return iter(self.objects)

    def __len__(self) -> int:
        """Return the number of selected scene objects."""
        return len(self._guids)

    @property
    def guids(self) -> tuple[UUID, ...]:
        """tuple[UUID, ...]: Selected stable object GUIDs in selection order."""
        return tuple(self._guids)

    @property
    def objects(self) -> tuple[SceneObject, ...]:
        """tuple[SceneObject, ...]: Selected objects resolved in selection order.

        Raises
        ------
        KeyError
            If the scene was mutated without cleaning a selected GUID.

        """
        return tuple(self._resolve(guid) for guid in self._guids)

    def replace(self, sceneobjects: Iterable[SceneObject]) -> bool:
        """Replace the selection with objects in the supplied order.

        Duplicate objects retain their first position.

        Parameters
        ----------
        sceneobjects
            Stable objects belonging to the current Viewer scene.

        Returns
        -------
        bool
            Whether the selection changed.

        Raises
        ------
        ValueError
            If an object does not belong to the current Viewer scene.

        """
        guids = self._validated_guids(sceneobjects)
        if tuple(self._guids) == guids:
            return False
        self._guids = dict.fromkeys(guids)
        self._notify()
        return True

    def add(self, *sceneobjects: SceneObject) -> bool:
        """Append objects not already selected.

        Parameters
        ----------
        *sceneobjects
            Stable objects belonging to the current Viewer scene.

        Returns
        -------
        bool
            Whether the selection changed.

        Raises
        ------
        ValueError
            If an object does not belong to the current Viewer scene.

        """
        guids = self._validated_guids(sceneobjects)
        additions = tuple(guid for guid in guids if guid not in self._guids)
        if not additions:
            return False
        self._guids.update(dict.fromkeys(additions))
        self._notify()
        return True

    def remove(self, *sceneobjects: SceneObject) -> bool:
        """Remove objects in one selection mutation.

        Objects that are not selected are ignored.

        Parameters
        ----------
        *sceneobjects
            Stable scene objects to remove. Objects that were just removed
            from the scene are accepted because removal uses their GUIDs
            without resolving them again.

        Returns
        -------
        bool
            Whether the selection changed.

        """
        remove = {sceneobject.guid for sceneobject in sceneobjects}
        if not remove.intersection(self._guids):
            return False
        self._guids = {guid: None for guid in self._guids if guid not in remove}
        self._notify()
        return True

    def toggle(self, sceneobject: SceneObject) -> bool:
        """Toggle one scene object while preserving the order of all others.

        Parameters
        ----------
        sceneobject
            Stable object belonging to the current Viewer scene.

        Returns
        -------
        bool
            The new selected state of `sceneobject`.

        Raises
        ------
        ValueError
            If `sceneobject` does not belong to the current Viewer scene.

        """
        guid = self._validated_guids((sceneobject,))[0]
        if guid in self._guids:
            del self._guids[guid]
            selected = False
        else:
            self._guids[guid] = None
            selected = True
        self._notify()
        return selected

    def clear(self) -> bool:
        """Clear the complete selection in one mutation.

        Returns
        -------
        bool
            Whether the selection changed.

        """
        if not self._guids:
            return False
        self._guids.clear()
        self._notify()
        return True

    def _validated_guids(self, sceneobjects: Iterable[SceneObject]) -> tuple[UUID, ...]:
        guids: dict[UUID, None] = {}
        for sceneobject in sceneobjects:
            try:
                resolved = self._resolve(sceneobject.guid)
            except KeyError as error:
                raise ValueError("Selection objects should belong to the current Viewer scene.") from error
            if resolved is not sceneobject:
                raise ValueError("Selection objects should belong to the current Viewer scene.")
            guids.setdefault(sceneobject.guid, None)
        return tuple(guids)

    def _notify(self) -> None:
        if self._changed is not None:
            self._changed(self.guids)


__all__ = ["Selection"]
