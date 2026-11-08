from dataclasses import FrozenInstanceError

import pytest

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import Translation
from compas.scene import SceneObject
from compas_viewer.snapping import ProjectedPoint
from compas_viewer.snapping import SnapKind
from compas_viewer.snapping import SurfaceHit
from compas_viewer.snapping import query_snap


def orthographic(point):
    return ProjectedPoint(point.x, point.y, point.z)


def test_snap_contract_is_immutable():
    sceneobject = SceneObject(Point(1, 2, 3))
    result = query_snap([sceneobject], (1, 2), radius=1, project=orthographic)

    assert result is not None
    with pytest.raises(FrozenInstanceError):
        setattr(result, "kind", SnapKind.LINE)
    with pytest.raises(AttributeError):
        setattr(SnapKind.POINT, "value", "changed")


def test_radius_is_inclusive_and_has_no_background_fallback():
    sceneobject = SceneObject(Point(3, 4, 0))

    result = query_snap([sceneobject], (0, 0), radius=5, project=orthographic)
    missing = query_snap([sceneobject], (0, 0), radius=4.99, project=orthographic)

    assert result is not None
    assert result.screen_distance == 5
    assert missing is None


def test_priority_precedes_screen_distance():
    line = SceneObject(Line([0, 0, 0], [10, 0, 0]))
    point = SceneObject(Point(2, 1, 0))

    result = query_snap([line, point], (2, 0), radius=2, project=orthographic)

    assert result is not None
    assert result.kind is SnapKind.POINT
    assert result.object_guid == point.guid


def test_nearest_candidate_wins_and_input_order_breaks_ties():
    first = SceneObject(Point(-1, 0, 0))
    second = SceneObject(Point(1, 0, 0))
    nearest = SceneObject(Point(0.25, 0, 0))

    result = query_snap([first, second, nearest], (0, 0), radius=2, project=orthographic)
    tie = query_snap([first, second], (0, 0), radius=2, project=orthographic)

    assert result is not None and result.object_guid == nearest.guid
    assert tie is not None and tie.object_guid == first.guid


def test_world_transformation_is_applied_before_projection():
    sceneobject = SceneObject(Point(1, 2, 3), transformation=Translation.from_vector([10, 20, 30]))

    result = query_snap([sceneobject], (11, 22), radius=0, project=orthographic)

    assert result is not None
    assert result.point == Point(11, 22, 33)


def test_perspective_segment_uses_normalized_world_parameter():
    line = SceneObject(Line([0, 0, 1], [10, 0, 10]))

    def perspective(point):
        return ProjectedPoint(point.x / point.z, point.y / point.z, point.z, point.z)

    result = query_snap([line], (0.5, 0), radius=0, project=perspective)

    assert result is not None
    assert result.kind is SnapKind.LINE
    assert result.parameter == pytest.approx(1 / 11)
    assert result.point == Point(10 / 11, 0, 20 / 11)
    anchor = result.component_anchor()
    assert anchor is not None
    assert anchor.parameter == pytest.approx(1 / 11)


def test_visibility_provider_rejects_occluded_candidates():
    occluded = SceneObject(Point(0, 0, 10))
    visible = SceneObject(Point(1, 0, 1))

    result = query_snap(
        [occluded, visible],
        (0, 0),
        radius=2,
        project=orthographic,
        is_visible=lambda projected: projected.depth < 5,
    )

    assert result is not None
    assert result.object_guid == visible.guid


def test_point_and_line_have_component_anchor_metadata():
    point = SceneObject(Point(0, 0, 0))
    line = SceneObject(Line([0, 0, 0], [10, 0, 0]))

    point_result = query_snap([point], (0, 0), radius=0, project=orthographic)
    line_result = query_snap([line], (2.5, 0), radius=0, project=orthographic)

    assert point_result is not None
    point_anchor = point_result.component_anchor()
    assert point_anchor is not None
    assert point_anchor.component_type == "point"
    assert line_result is not None
    line_anchor = line_result.component_anchor()
    assert line_anchor is not None
    assert line_anchor.component_type == "line"
    assert line_result.parameter == pytest.approx(0.25)


def test_mesh_vertex_and_edge_have_stable_component_metadata():
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [10, 0, 0], [0, 10, 0]], [[0, 1, 2]])
    sceneobject = SceneObject(mesh)

    vertex = query_snap([sceneobject], (0, 0), radius=0, project=orthographic)
    edge = query_snap([sceneobject], (5, 0), radius=0, project=orthographic)

    assert vertex is not None
    assert vertex.kind is SnapKind.VERTEX
    assert vertex.component == 0
    vertex_anchor = vertex.component_anchor()
    assert vertex_anchor is not None
    assert vertex_anchor.component == 0
    assert edge is not None
    assert edge.kind is SnapKind.EDGE
    assert edge.component == (0, 1)
    assert edge.parameter == pytest.approx(0.5)


def test_graph_node_and_edge_have_stable_component_metadata():
    graph = Graph()
    graph.add_node("a", x=0, y=0, z=0)
    graph.add_node(("group", 1), x=10, y=0, z=0)
    graph.add_edge("a", ("group", 1))
    sceneobject = SceneObject(graph)

    node = query_snap([sceneobject], (0, 0), radius=0, project=orthographic)
    edge = query_snap([sceneobject], (5, 0), radius=0, project=orthographic)

    assert node is not None
    assert node.kind is SnapKind.NODE
    assert node.component == "a"
    assert edge is not None
    assert edge.kind is SnapKind.EDGE
    assert edge.component == ("a", ("group", 1))
    assert edge.component_anchor() is not None


def test_nonserializable_graph_keys_are_visibly_not_associative():
    unstable_key = object()
    graph = Graph()
    graph.add_node(unstable_key, x=0, y=0, z=0)
    graph.add_node("stable", x=10, y=0, z=0)
    graph.add_edge(unstable_key, "stable")
    sceneobject = SceneObject(graph)

    node = query_snap([sceneobject], (0, 0), radius=0, project=orthographic)
    edge = query_snap([sceneobject], (5, 0), radius=0, project=orthographic)

    assert node is not None
    assert node.kind is SnapKind.NODE
    assert node.component is None
    assert not node.supports_association
    assert node.association_error is not None
    assert "stable serializable key" in node.association_error
    assert node.component_anchor() is None
    assert edge is not None
    assert edge.kind is SnapKind.EDGE
    assert edge.component is None
    assert not edge.supports_association
    assert edge.component_anchor() is None


def test_surface_hit_is_fixed_only_and_respects_visibility():
    sceneobject = SceneObject(Sphere(1))
    visible_hit = SurfaceHit(Point(0, 0, 1), sceneobject.guid, ProjectedPoint(1, 1, 1), SnapKind.FACE)
    occluded_hit = SurfaceHit(Point(0, 0, 5), sceneobject.guid, ProjectedPoint(0, 0, 5))

    result = query_snap(
        [sceneobject],
        (0, 0),
        radius=2,
        project=orthographic,
        is_visible=lambda projected: projected.depth < 2,
        surface_hits=lambda screen_point, radius: [occluded_hit, visible_hit],
    )

    assert result is not None
    assert result.kind is SnapKind.FACE
    assert result.point == Point(0, 0, 1)
    assert not result.supports_association
    assert result.association_error is not None
    assert "Face and surface" in result.association_error
    assert result.component_anchor() is None


def test_surface_hits_for_hidden_or_unlisted_objects_are_ignored():
    hidden = SceneObject(Sphere(1), show=False)
    unlisted = SceneObject(Sphere(1))
    hits = [
        SurfaceHit(Point(0, 0, 0), hidden.guid, ProjectedPoint(0, 0, 0)),
        SurfaceHit(Point(0, 0, 0), unlisted.guid, ProjectedPoint(0, 0, 0)),
    ]

    result = query_snap(
        [hidden],
        (0, 0),
        radius=1,
        project=orthographic,
        surface_hits=lambda screen_point, radius: hits,
    )

    assert result is None
