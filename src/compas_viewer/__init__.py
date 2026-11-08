"""Standalone OpenGL and Qt viewer for COMPAS geometry and data structures."""

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .animation import ANIMATION_PRESETS as ANIMATION_PRESETS
    from .animation import AnimationPreset as AnimationPreset
    from .commandregistry import CommandRegistry as CommandRegistry
    from .overlays import LegendOverlay as LegendOverlay
    from .overlays import ScaleBarOverlay as ScaleBarOverlay
    from .selection import Selection as Selection
    from .state import ViewerState as ViewerState
    from .viewer import Viewer as Viewer


__author__ = ["Li Chen"]
__copyright__ = "COMPAS Association"
__license__ = "MIT License"
__email__ = "li.chen@arch.ethz.ch"
__version__ = "2.0.2"


HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]
DATA = HOME / "data"
DOCS = HOME / "docs"
TEMP = HOME / "temp"


_LAZY_EXPORTS = {
    "ANIMATION_PRESETS": ("compas_viewer.animation", "ANIMATION_PRESETS"),
    "AnimationPreset": ("compas_viewer.animation", "AnimationPreset"),
    "CommandRegistry": ("compas_viewer.commandregistry", "CommandRegistry"),
    "LegendOverlay": ("compas_viewer.overlays", "LegendOverlay"),
    "ScaleBarOverlay": ("compas_viewer.overlays", "ScaleBarOverlay"),
    "Selection": ("compas_viewer.selection", "Selection"),
    "Viewer": ("compas_viewer.viewer", "Viewer"),
    "ViewerState": ("compas_viewer.state", "ViewerState"),
}


def __getattr__(name: str) -> object:
    """Load a public viewer object only when it is requested.

    This keeps plugin discovery independent of Qt and OpenGL while preserving
    direct imports such as `from compas_viewer import Viewer`.

    Parameters
    ----------
    name
        Public attribute name.

    Returns
    -------
    object
        Lazily imported public object.

    Raises
    ------
    AttributeError
        If `name` is not a public lazy export.

    """
    try:
        module_name, attribute_name = _LAZY_EXPORTS[name]
    except KeyError as error:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from error

    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value


__all__ = [
    "ANIMATION_PRESETS",
    "DATA",
    "DOCS",
    "HOME",
    "TEMP",
    "AnimationPreset",
    "CommandRegistry",
    "LegendOverlay",
    "ScaleBarOverlay",
    "Selection",
    "Viewer",
    "ViewerState",
]
