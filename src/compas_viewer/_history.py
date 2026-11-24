"""Private reversible Viewer transformation records."""

from dataclasses import dataclass

from compas.geometry import Transformation
from compas.scene import SceneObject

type TransformState = tuple[SceneObject, Transformation | None]


def copy_transformation(transformation: Transformation | None) -> Transformation | None:
    """Return an independent transformation while preserving `None`."""
    return transformation.copy() if transformation is not None else None


@dataclass(frozen=True, slots=True)
class TransformTransaction:
    """Before and after local transformations for one Viewer operation."""

    before: tuple[TransformState, ...]
    after: tuple[TransformState, ...]
