"""Standalone OpenGL and Qt viewer for COMPAS geometry and data structures."""

from pathlib import Path


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


from .viewer import Viewer  # noqa: F401, E402
from .animation import ANIMATION_PRESETS, AnimationPreset  # noqa: F401, E402
from .commandregistry import CommandRegistry  # noqa: F401, E402
from .state import ViewerState  # noqa: F401, E402

__all__ = ["ANIMATION_PRESETS", "DATA", "DOCS", "HOME", "TEMP", "AnimationPreset", "CommandRegistry", "Viewer", "ViewerState"]
