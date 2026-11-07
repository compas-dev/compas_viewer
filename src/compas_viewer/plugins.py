"""COMPAS plugin implementations provided by :mod:`compas_viewer`."""

import sys

from compas.plugins import plugin


@plugin(category="drawing-utils")
def clear(guids: list[object] | None = None) -> None:
    """Clear viewer objects.

    Parameters
    ----------
    guids
        The identifiers to clear. The viewer manages clearing through its scene,
        so this hook currently has no additional work to perform.

    """


@plugin(category="drawing-utils")
def before_draw() -> None:
    """Prepare the viewer before drawing a scene."""


@plugin(category="drawing-utils")
def after_draw(drawn_objects: list[object]) -> None:
    """Complete viewer drawing operations.

    Parameters
    ----------
    drawn_objects
        The objects drawn by the active scene.

    """


@plugin(category="factories")
def register_scene_operations() -> None:
    """Register lightweight Viewer draw and clear operations."""
    from compas.scene import SceneObject
    from compas.scene import register_scene_operation
    from compas_viewer.scene.runtime import clear
    from compas_viewer.scene.runtime import draw

    register_scene_operation("Viewer", SceneObject, "draw", draw)
    register_scene_operation("Viewer", SceneObject, "clear", clear)


def ensure_scene_objects_registered() -> None:
    """Ensure Viewer scene operations are available from source checkouts."""
    from compas.plugins import plugin_manager
    from compas.scene import SceneObject
    from compas.scene import register_scene_operations as register_all_scene_operations
    from compas.scene.context import SCENE_OPERATIONS

    operations = SCENE_OPERATIONS.get("Viewer", {}).get(SceneObject, {})
    if {"draw", "clear"} <= operations.keys():
        return

    plugin_manager.register_module(sys.modules[__name__])
    register_all_scene_operations()


__all__ = ["after_draw", "before_draw", "clear", "ensure_scene_objects_registered", "register_scene_operations"]
