"""Renderer-independent semantic snapping."""

from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from math import hypot
from typing import Literal
from typing import TypeGuard
from uuid import UUID

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import ComponentAnchor
from compas.scene import SceneItemNotBoundError
from compas.scene import SceneObject

__all__ = [
    "ProjectedPoint",
    "ProjectionProvider",
    "SnapKind",
    "SnapResult",
    "SurfaceHit",
    "SurfaceHitProvider",
    "VisibilityProvider",
    "query_snap",
]


type ScreenPoint = tuple[float, float]
type ComponentKey = int | str | tuple[ComponentKey, ...]
type EdgeKey = tuple[ComponentKey, ComponentKey]
type ComponentType = Literal["point", "vertex", "node", "line", "edge"]
type ProjectionProvider = Callable[[Point], "ProjectedPoint | None"]
type VisibilityProvider = Callable[["ProjectedPoint"], bool]
type SurfaceHitProvider = Callable[[ScreenPoint, float], Iterable["SurfaceHit"]]


_SURFACE_ASSOCIATION_ERROR = "Face and surface snaps do not support associative anchors."
_UNSTABLE_COMPONENT_ERROR = "The snapped component does not have a stable serializable key."


class SnapKind(StrEnum):
    """Semantic kind of a snapping result."""

    POINT = "point"
    VERTEX = "vertex"
    NODE = "node"
    LINE = "line"
    EDGE = "edge"
    FACE = "face"
    SURFACE = "surface"


@dataclass(frozen=True, slots=True)
class ProjectedPoint:
    """Screen projection of a world point.

    Parameters
    ----------
    x
        Horizontal screen coordinate in pixels.
    y
        Vertical screen coordinate in pixels.
    depth
        Depth value used by the visibility provider.
    clip_w
        Homogeneous clip-space $w$. A projection provider must return the
        actual value for perspective projections. It may use the default for
        orthographic projections.

    """

    x: float
    y: float
    depth: float
    clip_w: float = 1.0


@dataclass(frozen=True, slots=True)
class SurfaceHit:
    """One renderer-provided face or surface hit.

    Parameters
    ----------
    point
        Hit point in world coordinates.
    object_guid
        Stable GUID of the hit scene object.
    projection
        Screen projection and depth of the hit.
    kind
        Face or surface hit kind.

    """

    point: Point
    object_guid: UUID
    projection: ProjectedPoint
    kind: SnapKind = SnapKind.SURFACE


@dataclass(frozen=True, slots=True)
class SnapResult:
    """Resolved semantic snap.

    Parameters
    ----------
    point
        Resolved point in world coordinates.
    object_guid
        Stable GUID of the snapped scene object.
    kind
        Semantic snap kind.
    screen_distance
        Distance from the pointer in screen pixels.
    component
        Stable vertex, node, or edge component key, when applicable.
    parameter
        Normalized line or edge parameter, when applicable.
    association_error
        Reason the result cannot form an associative anchor, or `None` when
        association is supported.

    Notes
    -----
    Fixed acquisition can use every result's `point`. Associative acquisition
    must check `supports_association`; an unsupported result never contains a
    fallback point anchor.

    """

    point: Point
    object_guid: UUID
    kind: SnapKind
    screen_distance: float
    component: ComponentKey | EdgeKey | None = None
    parameter: float | None = None
    association_error: str | None = None

    @property
    def supports_association(self) -> bool:
        """Whether the result can form a durable component anchor."""
        return self.association_error is None

    def component_anchor(self) -> ComponentAnchor | None:
        """Return the durable component anchor, if supported.

        Returns
        -------
        ComponentAnchor | None
            A new associative anchor, or `None` for an unsupported result.

        """
        if not self.supports_association:
            return None
        component_type: ComponentType
        match self.kind:
            case SnapKind.POINT:
                component_type = "point"
            case SnapKind.VERTEX:
                component_type = "vertex"
            case SnapKind.NODE:
                component_type = "node"
            case SnapKind.LINE:
                component_type = "line"
            case SnapKind.EDGE:
                component_type = "edge"
            case _:
                return None
        return ComponentAnchor(
            self.object_guid,
            component_type,
            component=self.component,
            parameter=self.parameter,
        )


@dataclass(frozen=True, slots=True)
class _Candidate:
    point: Point
    object_guid: UUID
    kind: SnapKind
    projection: ProjectedPoint
    screen_distance: float
    component: ComponentKey | EdgeKey | None = None
    parameter: float | None = None
    association_error: str | None = None

    def result(self) -> SnapResult:
        return SnapResult(
            point=self.point,
            object_guid=self.object_guid,
            kind=self.kind,
            screen_distance=self.screen_distance,
            component=self.component,
            parameter=self.parameter,
            association_error=self.association_error,
        )


def query_snap(
    sceneobjects: Iterable[SceneObject],
    screen_point: ScreenPoint,
    *,
    radius: float,
    project: ProjectionProvider,
    is_visible: VisibilityProvider | None = None,
    surface_hits: SurfaceHitProvider | None = None,
) -> SnapResult | None:
    """Return the highest-priority semantic snap within a screen radius.

    Parameters
    ----------
    sceneobjects
        Stable scene objects eligible for snapping, in deterministic order.
    screen_point
        Pointer position in screen pixels.
    radius
        Inclusive snapping radius in screen pixels.
    project
        Renderer-provided world-to-screen projection.
    is_visible
        Optional renderer-provided depth or visibility test.
    surface_hits
        Optional renderer-provided face and surface hits.

    Returns
    -------
    SnapResult | None
        The nearest result in the highest available priority group, or `None`
        when no visible candidate is within the radius.

    Notes
    -----
    Priority is point, vertex, and node; then line and edge; then face and
    surface. Equal candidates retain input and component iteration order.

    """
    objects = tuple(sceneobjects)
    visible_guids = {sceneobject.guid for sceneobject in objects if sceneobject.show}
    candidates: list[_Candidate] = []
    for sceneobject in objects:
        if not sceneobject.show:
            continue
        candidates.extend(_object_candidates(sceneobject, screen_point, project))
    if surface_hits is not None:
        candidates.extend(_surface_candidates(surface_hits(screen_point, radius), screen_point, visible_guids))

    eligible = (candidate for candidate in candidates if candidate.screen_distance <= radius and (is_visible is None or is_visible(candidate.projection)))
    candidate = min(eligible, key=lambda item: (_priority(item.kind), item.screen_distance), default=None)
    return candidate.result() if candidate is not None else None


def _object_candidates(
    sceneobject: SceneObject,
    screen_point: ScreenPoint,
    project: ProjectionProvider,
) -> Iterable[_Candidate]:
    try:
        item = sceneobject.item
    except SceneItemNotBoundError:
        return ()
    if item is None:
        return ()

    transformation = sceneobject.worldtransformation
    if isinstance(item, Point):
        point = item.transformed(transformation)
        candidate = _point_candidate(point, sceneobject.guid, SnapKind.POINT, screen_point, project)
        return (candidate,) if candidate is not None else ()
    if isinstance(item, Line):
        start = item.start.transformed(transformation)
        end = item.end.transformed(transformation)
        candidate = _segment_candidate(start, end, sceneobject.guid, SnapKind.LINE, screen_point, project)
        return (candidate,) if candidate is not None else ()
    if isinstance(item, Mesh):
        points = ((key, item.vertex_point(key).transformed(transformation)) for key in item.vertices())
        return _network_candidates(sceneobject.guid, SnapKind.VERTEX, points, item.edges(), screen_point, project)
    if isinstance(item, Graph):
        points = ((key, item.node_point(key).transformed(transformation)) for key in item.nodes())
        return _network_candidates(sceneobject.guid, SnapKind.NODE, points, item.edges(), screen_point, project)
    return ()


def _network_candidates(
    object_guid: UUID,
    point_kind: SnapKind,
    keyed_points: Iterable[tuple[object, Point]],
    edges: Iterable[tuple[object, object]],
    screen_point: ScreenPoint,
    project: ProjectionProvider,
) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    points: dict[object, tuple[Point, ProjectedPoint | None]] = {}
    for key, point in keyed_points:
        projection = project(point)
        points[key] = point, projection
        candidate = _point_candidate_from_projection(
            point,
            object_guid,
            point_kind,
            key,
            projection,
            screen_point,
        )
        if candidate is not None:
            candidates.append(candidate)

    for edge in edges:
        start, end = edge
        start_point, start_projection = points[start]
        end_point, end_projection = points[end]
        candidate = _segment_candidate_from_projections(
            start_point,
            end_point,
            object_guid,
            SnapKind.EDGE,
            screen_point,
            start_projection,
            end_projection,
            component=edge,
        )
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _point_candidate(
    point: Point,
    object_guid: UUID,
    kind: SnapKind,
    screen_point: ScreenPoint,
    project: ProjectionProvider,
) -> _Candidate | None:
    return _point_candidate_from_projection(point, object_guid, kind, None, project(point), screen_point)


def _point_candidate_from_projection(
    point: Point,
    object_guid: UUID,
    kind: SnapKind,
    raw_component: object,
    projection: ProjectedPoint | None,
    screen_point: ScreenPoint,
) -> _Candidate | None:
    if projection is None:
        return None
    component: ComponentKey | None = None
    association_error = None
    if kind in {SnapKind.VERTEX, SnapKind.NODE}:
        if _is_component_key(raw_component):
            component = raw_component
        else:
            association_error = _UNSTABLE_COMPONENT_ERROR
    return _Candidate(
        point,
        object_guid,
        kind,
        projection,
        _screen_distance(projection, screen_point),
        component=component,
        association_error=association_error,
    )


def _segment_candidate(
    start: Point,
    end: Point,
    object_guid: UUID,
    kind: SnapKind,
    screen_point: ScreenPoint,
    project: ProjectionProvider,
) -> _Candidate | None:
    return _segment_candidate_from_projections(
        start,
        end,
        object_guid,
        kind,
        screen_point,
        project(start),
        project(end),
    )


def _segment_candidate_from_projections(
    start: Point,
    end: Point,
    object_guid: UUID,
    kind: SnapKind,
    screen_point: ScreenPoint,
    start_projection: ProjectedPoint | None,
    end_projection: ProjectedPoint | None,
    *,
    component: tuple[object, object] | None = None,
) -> _Candidate | None:
    if start_projection is None or end_projection is None:
        return None
    screen_parameter = _closest_segment_parameter(start_projection, end_projection, screen_point)
    parameter = _perspective_parameter(screen_parameter, start_projection.clip_w, end_projection.clip_w)
    if parameter is None:
        return None
    point = Point(
        start.x + parameter * (end.x - start.x),
        start.y + parameter * (end.y - start.y),
        start.z + parameter * (end.z - start.z),
    )
    projection = ProjectedPoint(
        start_projection.x + screen_parameter * (end_projection.x - start_projection.x),
        start_projection.y + screen_parameter * (end_projection.y - start_projection.y),
        start_projection.depth + screen_parameter * (end_projection.depth - start_projection.depth),
        start_projection.clip_w + parameter * (end_projection.clip_w - start_projection.clip_w),
    )
    stable_component: EdgeKey | None = None
    association_error = None
    if component is not None:
        if _is_component_key(component[0]) and _is_component_key(component[1]):
            stable_component = (component[0], component[1])
        else:
            association_error = _UNSTABLE_COMPONENT_ERROR
    return _Candidate(
        point,
        object_guid,
        kind,
        projection,
        _screen_distance(projection, screen_point),
        component=stable_component,
        parameter=parameter,
        association_error=association_error,
    )


def _surface_candidates(
    hits: Iterable[SurfaceHit],
    screen_point: ScreenPoint,
    visible_guids: set[UUID],
) -> Iterable[_Candidate]:
    for hit in hits:
        if hit.object_guid not in visible_guids or hit.kind not in {SnapKind.FACE, SnapKind.SURFACE}:
            continue
        yield _Candidate(
            Point(hit.point.x, hit.point.y, hit.point.z),
            hit.object_guid,
            hit.kind,
            hit.projection,
            _screen_distance(hit.projection, screen_point),
            association_error=_SURFACE_ASSOCIATION_ERROR,
        )


def _closest_segment_parameter(start: ProjectedPoint, end: ProjectedPoint, point: ScreenPoint) -> float:
    dx = end.x - start.x
    dy = end.y - start.y
    squared_length = dx * dx + dy * dy
    if squared_length == 0.0:
        return 0.0
    parameter = ((point[0] - start.x) * dx + (point[1] - start.y) * dy) / squared_length
    return max(0.0, min(1.0, parameter))


def _perspective_parameter(screen_parameter: float, start_w: float, end_w: float) -> float | None:
    if start_w == 0.0 or end_w == 0.0:
        return None
    denominator = (1.0 - screen_parameter) / start_w + screen_parameter / end_w
    if denominator == 0.0:
        return None
    return (screen_parameter / end_w) / denominator


def _screen_distance(projection: ProjectedPoint, point: ScreenPoint) -> float:
    return hypot(projection.x - point[0], projection.y - point[1])


def _priority(kind: SnapKind) -> int:
    if kind in {SnapKind.POINT, SnapKind.VERTEX, SnapKind.NODE}:
        return 0
    if kind in {SnapKind.LINE, SnapKind.EDGE}:
        return 1
    return 2


def _is_component_key(value: object) -> TypeGuard[ComponentKey]:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, str)):
        return True
    return isinstance(value, tuple) and all(_is_component_key(item) for item in value)
