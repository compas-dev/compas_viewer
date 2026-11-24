"""Resolve durable distance-dimension layout for Viewer presentation."""

from dataclasses import dataclass
from typing import Any

from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import DistanceDimension
from compas.scene import SceneAnnotation
from compas.tolerance import TOL


@dataclass(frozen=True)
class DimensionLayoutResolution:
    """Resolved Viewer presentation for one distance dimension."""

    status: str
    anchors: tuple[Point, Point] | None
    line_points: tuple[Point, Point] | None
    displaced: bool = False


def resolve_dimension_layout(annotation: SceneAnnotation, runtime_scene: Any) -> DimensionLayoutResolution:
    """Resolve the selected annotation's deterministic world-space layout."""
    item = annotation.item
    if not isinstance(item, DistanceDimension):
        raise TypeError("Distance-dimension layout requires a DistanceDimension annotation.")
    layout = annotation.layout
    if layout is None:
        raise RuntimeError("Bound distance-dimension annotations require a layout.")

    anchors = item.resolve(runtime_scene)
    if TOL.is_zero(layout.offset):
        return DimensionLayoutResolution("Resolved — no displacement", anchors, anchors)
    if anchors is None:
        return DimensionLayoutResolution("Unresolved — dimension anchor is unresolved", None, None)

    segment = Vector.from_start_end(anchors[0], anchors[1])
    if TOL.is_zero(segment.length):
        return DimensionLayoutResolution("Unresolved — anchors coincide", anchors, anchors)
    normal = layout.plane_normal
    if normal is None:
        return DimensionLayoutResolution("Unresolved — plane normal is missing", anchors, anchors)
    if TOL.is_zero(normal.length):
        return DimensionLayoutResolution("Unresolved — plane normal is zero", anchors, anchors)
    direction = normal.cross(segment)
    if TOL.is_zero(direction.length):
        return DimensionLayoutResolution("Unresolved — plane normal is parallel to dimension", anchors, anchors)

    direction.unitize()
    displacement = direction * layout.offset
    line_points = (anchors[0] + displacement, anchors[1] + displacement)
    return DimensionLayoutResolution("Resolved", anchors, line_points, displaced=True)


__all__ = ["DimensionLayoutResolution", "resolve_dimension_layout"]
