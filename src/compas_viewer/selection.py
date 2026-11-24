from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Protocol
from uuid import UUID


class Selectable(Protocol):
    """Structurally selectable value with a stable GUID."""

    @property
    def guid(self) -> UUID:
        """Stable identity used by the selection."""
        ...


class Selection[T: Selectable]:
    """Store one ordered Viewer selection independently of Qt and scene data.

    Parameters
    ----------
    resolve
        Resolve a stable value GUID in the current Viewer scene.
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
        resolve: Callable[[UUID], T],
        changed: Callable[[tuple[UUID, ...]], None] | None = None,
    ) -> None:
        self._resolve = resolve
        self._changed = changed
        self._guids: dict[UUID, None] = {}

    def __bool__(self) -> bool:
        """Return whether at least one value is selected."""
        return bool(self._guids)

    def __contains__(self, value: T | UUID) -> bool:
        """Return whether a resolved value or GUID is selected."""
        guid = value if isinstance(value, UUID) else value.guid
        return guid in self._guids

    def __iter__(self) -> Iterator[T]:
        """Iterate over selected values in selection order."""
        return iter(self.objects)

    def __len__(self) -> int:
        """Return the number of selected values."""
        return len(self._guids)

    @property
    def guids(self) -> tuple[UUID, ...]:
        """tuple[UUID, ...]: Selected stable object GUIDs in selection order."""
        return tuple(self._guids)

    @property
    def objects(self) -> tuple[T, ...]:
        """tuple[T, ...]: Selected values resolved in selection order.

        Raises
        ------
        KeyError
            If the scene was mutated without cleaning a selected GUID.

        """
        return tuple(self._resolve(guid) for guid in self._guids)

    def replace(self, values: Iterable[T]) -> bool:
        """Replace the selection with objects in the supplied order.

        Duplicate objects retain their first position.

        Parameters
        ----------
        values
            Stable values belonging to the current Viewer scene.

        Returns
        -------
        bool
            Whether the selection changed.

        Raises
        ------
        ValueError
            If an object does not belong to the current Viewer scene.

        """
        guids = self._validated_guids(values)
        if tuple(self._guids) == guids:
            return False
        self._guids = dict.fromkeys(guids)
        self._notify()
        return True

    def add(self, *values: T) -> bool:
        """Append objects not already selected.

        Parameters
        ----------
        *values
            Stable values belonging to the current Viewer scene.

        Returns
        -------
        bool
            Whether the selection changed.

        Raises
        ------
        ValueError
            If an object does not belong to the current Viewer scene.

        """
        guids = self._validated_guids(values)
        additions = tuple(guid for guid in guids if guid not in self._guids)
        if not additions:
            return False
        self._guids.update(dict.fromkeys(additions))
        self._notify()
        return True

    def remove(self, *values: T) -> bool:
        """Remove objects in one selection mutation.

        Objects that are not selected are ignored.

        Parameters
        ----------
        *values
            Stable values to remove. Values that were just removed
            from the scene are accepted because removal uses their GUIDs
            without resolving them again.

        Returns
        -------
        bool
            Whether the selection changed.

        """
        remove = {value.guid for value in values}
        if not remove.intersection(self._guids):
            return False
        self._guids = {guid: None for guid in self._guids if guid not in remove}
        self._notify()
        return True

    def toggle(self, value: T) -> bool:
        """Toggle one value while preserving the order of all others.

        Parameters
        ----------
        value
            Stable value belonging to the current Viewer scene.

        Returns
        -------
        bool
            The new selected state of `value`.

        Raises
        ------
        ValueError
            If `value` does not belong to the current Viewer scene.

        """
        guid = self._validated_guids((value,))[0]
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

    def _validated_guids(self, values: Iterable[T]) -> tuple[UUID, ...]:
        guids: dict[UUID, None] = {}
        for value in values:
            try:
                resolved = self._resolve(value.guid)
            except KeyError as error:
                raise ValueError("Selection values should belong to the current Viewer scene.") from error
            if resolved is not value:
                raise ValueError("Selection values should belong to the current Viewer scene.")
            guids.setdefault(value.guid, None)
        return tuple(guids)

    def _notify(self) -> None:
        if self._changed is not None:
            self._changed(self.guids)


__all__ = ["Selectable", "Selection"]
