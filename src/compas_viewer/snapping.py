"""Renderer-independent semantic snapping."""

from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from math import hypot
from typing import TypeGuard
from uuid import UUID

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Point
from compas.scene import ComponentAnchor
from compas.scene import SceneItemNotBoundError
from compas.scene import SceneObject

__all__ = [
    "ProjectedPoint",
    "ProjectionProvider",
    "SnapKind",
    "SnapQuery",
    "SnapResult",
    "VisibilityProvider",
    "query_snap",
    "query_snaps",
]


type ScreenPoint = tuple[float, float]
type ComponentKey = int | str | tuple[ComponentKey, ...]
type ProjectionProvider = Callable[[Point], "ProjectedPoint | None"]
type VisibilityProvider = Callable[["ProjectedPoint"], bool]


_UNSTABLE_COMPONENT_ERROR = "The snapped component does not have a stable serializable key."


class SnapKind(StrEnum):
    """Semantic kind of a snapping result."""

    POINT = "point"
    VERTEX = "vertex"
    NODE = "node"


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

    """

    x: float
    y: float
    depth: float


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
        Stable vertex or node component key, when applicable.
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
    component: ComponentKey | None = None
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
        match self.kind:
            case SnapKind.POINT:
                return ComponentAnchor(self.object_guid, "point")
            case SnapKind.VERTEX:
                return ComponentAnchor(self.object_guid, "vertex", component=self.component)
            case SnapKind.NODE:
                return ComponentAnchor(self.object_guid, "node", component=self.component)


@dataclass(frozen=True, slots=True)
class SnapQuery:
    """One measurement hover query.

    Parameters
    ----------
    winner
        Depth-qualified result that a click will accept, or `None` when no
        candidate lies within the acquisition radius.
    points
        All projected discrete point snaps of the hovered object. These points
        guide the user toward available snaps; they are not independently
        depth-qualified and are not accepted unless one becomes `winner`.

    """

    winner: SnapResult | None = None
    points: tuple[SnapResult, ...] = ()


@dataclass(frozen=True, slots=True)
class _Candidate:
    point: Point
    object_guid: UUID
    kind: SnapKind
    projection: ProjectedPoint
    screen_distance: float
    component: ComponentKey | None = None
    association_error: str | None = None

    def result(self) -> SnapResult:
        return SnapResult(
            point=self.point,
            object_guid=self.object_guid,
            kind=self.kind,
            screen_distance=self.screen_distance,
            component=self.component,
            association_error=self.association_error,
        )


def query_snap(
    sceneobjects: Iterable[SceneObject],
    screen_point: ScreenPoint,
    *,
    radius: float,
    project: ProjectionProvider,
    is_visible: VisibilityProvider | None = None,
) -> SnapResult | None:
    """Return the nearest visible discrete snap within a screen radius.

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

    Returns
    -------
    SnapResult | None
        The nearest visible discrete result, or `None` when no candidate is
        within the radius.

    Notes
    -----
    Interactive acquisition is limited to Point objects, Mesh vertices, and
    Graph nodes. Equal candidates retain input and component iteration order.

    """
    return query_snaps(
        sceneobjects,
        screen_point,
        radius=radius,
        project=project,
        is_visible=is_visible,
    ).winner


def query_snaps(
    sceneobjects: Iterable[SceneObject],
    screen_point: ScreenPoint,
    *,
    radius: float,
    project: ProjectionProvider,
    is_visible: VisibilityProvider | None = None,
) -> SnapQuery:
    """Return one winner and all discrete point snaps from one candidate pass.

    Parameters
    ----------
    sceneobjects
        Stable scene objects eligible for snapping, in deterministic order.
        Measurement hover supplies one object.
    screen_point
        Pointer position in screen pixels.
    radius
        Inclusive acquisition radius in screen pixels.
    project
        Renderer-provided world-to-screen projection.
    is_visible
        Optional renderer-provided depth or visibility test for the winner.

    Returns
    -------
    SnapQuery
        Nearest depth-qualified winner and every projected Point, Mesh-vertex,
        or Graph-node candidate. Palette points are collected before radius and
        visibility filtering and are display guidance only.

    """
    objects = tuple(sceneobjects)
    candidates: list[_Candidate] = []
    for sceneobject in objects:
        if not sceneobject.show:
            continue
        candidates.extend(_object_candidates(sceneobject, screen_point, project))
    points = tuple(candidate.result() for candidate in candidates)

    eligible = (candidate for candidate in candidates if candidate.screen_distance <= radius and (is_visible is None or is_visible(candidate.projection)))
    candidate = min(eligible, key=lambda item: item.screen_distance, default=None)
    return SnapQuery(candidate.result() if candidate is not None else None, points)


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
    if isinstance(item, Mesh):
        points = ((key, item.vertex_point(key).transformed(transformation)) for key in item.vertices())
        return _network_candidates(sceneobject.guid, SnapKind.VERTEX, points, screen_point, project)
    if isinstance(item, Graph):
        points = ((key, item.node_point(key).transformed(transformation)) for key in item.nodes())
        return _network_candidates(sceneobject.guid, SnapKind.NODE, points, screen_point, project)
    return ()


def _network_candidates(
    object_guid: UUID,
    point_kind: SnapKind,
    keyed_points: Iterable[tuple[object, Point]],
    screen_point: ScreenPoint,
    project: ProjectionProvider,
) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for key, point in keyed_points:
        projection = project(point)
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


def _screen_distance(projection: ProjectedPoint, point: ScreenPoint) -> float:
    return hypot(projection.x - point[0], projection.y - point[1])


def _is_component_key(value: object) -> TypeGuard[ComponentKey]:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, str)):
        return True
    return isinstance(value, tuple) and all(_is_component_key(item) for item in value)
