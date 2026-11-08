"""Contextual editable-attribute contributions for stable scene objects."""

from collections.abc import Callable
from collections.abc import Mapping
from inspect import getattr_static
from inspect import getmro
from types import MappingProxyType
from typing import Any
from typing import Final
from typing import cast

from compas.plugins import pluggable
from compas.scene import SceneObject

type AttributeUpdate[SceneObjectT: SceneObject] = Callable[[SceneObjectT, object], None]
type AttributeContribution[SceneObjectT: SceneObject] = Mapping[str, AttributeUpdate[SceneObjectT] | None | _RemoveEditableAttribute]


class _RemoveEditableAttribute:
    """Marker for removing an attribute from a contextual inventory."""


REMOVE_EDITABLE_ATTRIBUTE: Final = _RemoveEditableAttribute()
"""Explicit marker for removing a contextual editable attribute."""


_CONTRIBUTIONS: dict[
    tuple[str, type[SceneObject], str],
    Mapping[str, Callable[[Any, object], None] | None | _RemoveEditableAttribute],
] = {}
_CONTRIBUTIONS_DISCOVERED = False


@pluggable(category="factories", selector="collect_all")
def register_scene_attribute_contributions() -> None:
    """Register contextual editable-attribute contributions from plugins."""
    raise NotImplementedError


def register_scene_attribute_contribution[SceneObjectT: SceneObject](
    context: str,
    sceneobject_type: type[SceneObjectT],
    contribution: str,
    attributes: AttributeContribution[SceneObjectT],
) -> None:
    """Register one contextual editable-attribute contribution.

    Parameters
    ----------
    context
        Visualization context receiving the contribution.
    sceneobject_type
        Stable scene-object type to which the contribution applies.
    contribution
        Stable contribution identifier.
    attributes
        Ordered mapping from flat attribute names to update callbacks. `None`
        selects ordinary assignment. `REMOVE_EDITABLE_ATTRIBUTE` removes an
        inherited attribute.

    Raises
    ------
    TypeError
        If the type, mapping, names, or values are invalid.
    ValueError
        If a key part is empty or the exact key is already registered.

    """
    if not context:
        raise ValueError("A scene-attribute context should be a non-empty string.")
    if not isinstance(sceneobject_type, type) or not issubclass(sceneobject_type, SceneObject):
        raise TypeError("A scene-attribute contribution requires a stable SceneObject type.")
    if not contribution:
        raise ValueError("A scene-attribute contribution ID should be a non-empty string.")
    if not isinstance(attributes, Mapping):
        raise TypeError("A scene-attribute contribution should be a mapping.")
    for name, update in attributes.items():
        if not isinstance(name, str):
            raise TypeError("Scene-attribute contribution names should be strings.")
        if not name or "." in name:
            raise ValueError("A scene-attribute contribution name should be one flat public name.")
        if update is not None and update is not REMOVE_EDITABLE_ATTRIBUTE and not callable(update):
            raise TypeError("A scene-attribute contribution value should be callable, None, or REMOVE_EDITABLE_ATTRIBUTE.")
    key = (context, sceneobject_type, contribution)
    if key in _CONTRIBUTIONS:
        raise ValueError(f"Scene-attribute contribution already registered: {context}/{sceneobject_type.__name__}/{contribution}.")
    _CONTRIBUTIONS[key] = MappingProxyType(
        cast(
            dict[str, Callable[[Any, object], None] | None | _RemoveEditableAttribute],
            dict(attributes),
        )
    )


def scene_editable_attributes[SceneObjectT: SceneObject](
    context: str,
    sceneobject: SceneObjectT,
) -> Mapping[str, AttributeUpdate[SceneObjectT] | None]:
    """Resolve editable attributes for one context and stable scene object.

    Parameters
    ----------
    context
        Visualization context requesting the inventory.
    sceneobject
        Stable scene object being edited.

    Returns
    -------
    Mapping[str, AttributeUpdate[SceneObjectT] | None]
        Read-only ordered mapping of attribute names to optional update
        callbacks.

    Raises
    ------
    ValueError
        If contributions at the same specificity modify the same attribute.

    """
    _ensure_contributions_discovered()
    resolved = dict(sceneobject.editable_attributes())
    mro = getmro(type(sceneobject))
    applicable = sorted(
        (
            (len(mro) - mro.index(owner), contribution, owner, attributes)
            for (registered_context, owner, contribution), attributes in _CONTRIBUTIONS.items()
            if registered_context == context and owner in mro
        ),
        key=lambda entry: (entry[0], entry[1]),
    )
    touched: dict[tuple[int, str], str] = {}
    for rank, contribution, owner, attributes in applicable:
        for name, update in attributes.items():
            conflict_key = (rank, name)
            if conflict_key in touched:
                first = touched[conflict_key]
                raise ValueError(f"Conflicting scene-attribute contributions for {context}/{owner.__name__}/{name}: {first} and {contribution}.")
            touched[conflict_key] = contribution
            if update is REMOVE_EDITABLE_ATTRIBUTE:
                resolved.pop(name, None)
            else:
                resolved[name] = cast(Callable[[SceneObject, object], None] | None, update)
    writable = {name: update for name, update in resolved.items() if update is not None or _supports_ordinary_assignment(sceneobject, name)}
    return MappingProxyType(cast(dict[str, AttributeUpdate[SceneObjectT] | None], writable))


def _supports_ordinary_assignment(sceneobject: SceneObject, name: str) -> bool:
    """Return whether ordinary assignment can update an attribute."""
    missing = object()
    descriptor = getattr_static(type(sceneobject), name, missing)
    return not isinstance(descriptor, property) or descriptor.fset is not None


def _ensure_contributions_discovered() -> None:
    """Discover installed contributions once without importing graphics."""
    global _CONTRIBUTIONS_DISCOVERED
    if _CONTRIBUTIONS_DISCOVERED:
        return
    register_scene_attribute_contributions()
    _CONTRIBUTIONS_DISCOVERED = True


__all__ = [
    "AttributeContribution",
    "AttributeUpdate",
    "REMOVE_EDITABLE_ATTRIBUTE",
    "register_scene_attribute_contribution",
    "register_scene_attribute_contributions",
    "scene_editable_attributes",
]
