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
from compas_viewer.snapping import SnapQuery
from compas_viewer.snapping import query_snap
from compas_viewer.snapping import query_snaps


def orthographic(point):
    return ProjectedPoint(point.x, point.y, point.z)


def test_snap_contract_is_immutable():
    sceneobject = SceneObject(Point(1, 2, 3))
    result = query_snap([sceneobject], (1, 2), radius=1, project=orthographic)

    assert result is not None
    with pytest.raises(FrozenInstanceError):
        setattr(result, "kind", SnapKind.NODE)
    with pytest.raises(AttributeError):
        setattr(SnapKind.POINT, "value", "changed")
    with pytest.raises(FrozenInstanceError):
        setattr(SnapQuery(result, (result,)), "winner", None)


def test_hover_palette_contains_all_discrete_points_in_component_order():
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [10, 0, 0], [0, 10, 0]], [[0, 1, 2]])
    sceneobject = SceneObject(mesh, transformation=Translation.from_vector([1, 2, 3]))

    points = query_snaps([sceneobject], (0, 0), radius=0, project=orthographic).points

    assert [point.kind for point in points] == [SnapKind.VERTEX] * 3
    assert [point.component for point in points] == [0, 1, 2]
    assert [point.point for point in points] == [Point(1, 2, 3), Point(11, 2, 3), Point(1, 12, 3)]


def test_hover_palette_supports_only_points_mesh_vertices_and_graph_nodes():
    point = SceneObject(Point(1, 2, 3))
    line = SceneObject(Line([0, 0, 0], [10, 0, 0]))
    sphere = SceneObject(Sphere(1))
    graph = Graph()
    graph.add_node("a", x=0, y=0, z=0)
    graph.add_node("b", x=1, y=0, z=0)
    graph.add_edge("a", "b")

    point_snaps = query_snaps([point], (0, 0), radius=0, project=orthographic).points
    line_query = query_snaps([line], (0, 0), radius=10, project=orthographic)
    sphere_query = query_snaps([sphere], (0, 0), radius=10, project=orthographic)
    node_query = query_snaps([SceneObject(graph)], (0, 0), radius=0, project=orthographic)

    assert [snap.kind for snap in point_snaps] == [SnapKind.POINT]
    assert line_query == SnapQuery()
    assert sphere_query == SnapQuery()
    assert [snap.kind for snap in node_query.points] == [SnapKind.NODE, SnapKind.NODE]
    assert [snap.component for snap in node_query.points] == ["a", "b"]


def test_radius_is_inclusive_and_has_no_background_fallback():
    sceneobject = SceneObject(Point(3, 4, 0))

    result = query_snap([sceneobject], (0, 0), radius=5, project=orthographic)
    missing = query_snap([sceneobject], (0, 0), radius=4.99, project=orthographic)

    assert result is not None
    assert result.screen_distance == 5
    assert missing is None


def test_unsupported_line_does_not_compete_with_discrete_point():
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


def test_point_acquisition_has_component_anchor_metadata():
    point = SceneObject(Point(0, 0, 0))

    point_result = query_snap([point], (0, 0), radius=0, project=orthographic)

    assert point_result is not None
    point_anchor = point_result.component_anchor()
    assert point_anchor is not None
    assert point_anchor.component_type == "point"


def test_mesh_vertices_have_stable_metadata_without_edge_acquisition():
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
    assert edge is None


def test_graph_nodes_have_stable_metadata_without_edge_acquisition():
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
    assert edge is None


def test_nonserializable_graph_keys_are_visibly_not_associative():
    unstable_key = object()
    graph = Graph()
    graph.add_node(unstable_key, x=0, y=0, z=0)
    graph.add_node("stable", x=10, y=0, z=0)
    graph.add_edge(unstable_key, "stable")
    sceneobject = SceneObject(graph)

    node = query_snap([sceneobject], (0, 0), radius=0, project=orthographic)
    assert node is not None
    assert node.kind is SnapKind.NODE
    assert node.component is None
    assert not node.supports_association
    assert node.association_error is not None
    assert "stable serializable key" in node.association_error
    assert node.component_anchor() is None


def test_mesh_has_no_face_or_edge_fallback_when_no_vertex_is_in_range():
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [4, 0, 0], [4, 3, 0], [0, 3, 0]], [[0, 1, 2, 3]])
    sceneobject = SceneObject(mesh)

    query = query_snaps(
        [sceneobject],
        (2, 1.5),
        radius=0.5,
        project=orthographic,
    )

    assert query.winner is None
    assert [snap.kind for snap in query.points] == [SnapKind.VERTEX] * 4


def test_hidden_discrete_object_has_no_candidates():
    assert query_snap([SceneObject(Point(0, 0, 0), show=False)], (0, 0), radius=1, project=orthographic) is None
