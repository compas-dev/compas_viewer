import numpy as np
import pytest

from compas.data import json_dumps
from compas.data import json_loads
from compas_viewer import Viewer
from compas_viewer.scene import BufferGeometry


@pytest.fixture
def viewer(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    viewer = Viewer()
    viewer.running = False
    viewer.scene.clear(clear_context=False)
    yield viewer
    viewer.running = False
    viewer.scene.clear(clear_context=False)


def test_buffergeometry_normalizes_and_copies_structural_inputs():
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
    triangles = [[0, 1, 2]]

    geometry = BufferGeometry.from_vertices_and_triangles(vertices, triangles)
    vertices[0, 0] = 10
    triangles[0][0] = 2

    assert geometry.triangles is not None
    assert geometry.vertices.dtype == np.float32
    assert geometry.triangles.dtype == np.int32
    assert geometry.vertices.flags.c_contiguous
    assert geometry.triangles.flags.c_contiguous
    np.testing.assert_array_equal(geometry.vertices, [[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    np.testing.assert_array_equal(geometry.triangles, [[0, 1, 2]])
    np.testing.assert_array_equal(geometry.facecolor, np.ones((3, 4), dtype=np.float32))


def test_buffergeometry_convenience_constructors_select_one_index_channel():
    vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]

    points = BufferGeometry.from_points(vertices)
    edges = BufferGeometry.from_vertices_and_edges(vertices, [[0, 1], [1, 2]])
    triangles = BufferGeometry.from_vertices_and_triangles(vertices, [[0, 1, 2]])

    np.testing.assert_array_equal(points.points, [0, 1, 2])
    assert points.edges is None
    np.testing.assert_array_equal(edges.edges, [[0, 1], [1, 2]])
    assert edges.triangles is None
    np.testing.assert_array_equal(triangles.triangles, [[0, 1, 2]])
    assert triangles.points is None


def test_buffergeometry_accepts_empty_index_channels():
    geometry = BufferGeometry([[0, 0, 0]], points=[], edges=[], triangles=[])

    assert geometry.points is not None
    assert geometry.edges is not None
    assert geometry.triangles is not None
    assert geometry.points.shape == (0,)
    assert geometry.edges.shape == (0, 2)
    assert geometry.triangles.shape == (0, 3)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"vertices": [0, 0, 0]}, "Vertices should have shape"),
        ({"vertices": [[0, 0, 0]], "points": [[0]]}, "Points should have shape"),
        ({"vertices": [[0, 0, 0]], "edges": [[0, 0, 0]]}, "Edges should have shape"),
        ({"vertices": [[0, 0, 0]], "triangles": [[0, 0]]}, "Triangles should have shape"),
        ({"vertices": [[0, 0, 0]], "points": [0.5]}, "integral vertex indices"),
        ({"vertices": [[0, 0, 0]], "edges": [[0, float("nan")]]}, "integral vertex indices"),
        ({"vertices": [[0, 0, 0]], "points": [1]}, "outside"),
        ({"vertices": [[0, 0, 0]], "edges": [[-1, 0]]}, "outside"),
        ({"vertices": [[0, 0, 0]], "facecolor": [[1, 1, 1]]}, "one color per vertex"),
    ],
)
def test_buffergeometry_rejects_invalid_shapes_and_bounds(kwargs, message):
    with pytest.raises(ValueError, match=message):
        BufferGeometry(**kwargs)


def test_buffergeometry_has_an_independent_json_roundtrip():
    original = BufferGeometry(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        points=[0],
        edges=[[0, 1]],
        triangles=[[0, 1, 2]],
        facecolor=[[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]],
    )

    restored = json_loads(json_dumps(original))

    assert isinstance(restored, BufferGeometry)
    np.testing.assert_array_equal(restored.vertices, original.vertices)
    np.testing.assert_array_equal(restored.points, original.points)
    np.testing.assert_array_equal(restored.edges, original.edges)
    np.testing.assert_array_equal(restored.triangles, original.triangles)
    np.testing.assert_array_equal(restored.facecolor, original.facecolor)


def test_buffergeometry_accepts_integral_python_and_numpy_indices():
    geometry = BufferGeometry(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        points=[0.0, 1.0],
        edges=np.array([[0, 1]], dtype=np.uint16),
        triangles=np.array([[0, 1, 2]], dtype=np.int64),
    )

    assert geometry.points is not None
    assert geometry.edges is not None
    assert geometry.triangles is not None
    assert geometry.points.dtype == np.int32
    assert geometry.edges.dtype == np.int32
    assert geometry.triangles.dtype == np.int32


def test_bufferobject_preserves_shared_vertices_and_indices(viewer):
    geometry = BufferGeometry(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        points=[0, 3],
        edges=[[0, 1], [2, 3]],
        triangles=[[0, 1, 2], [1, 3, 2]],
    )
    sceneobject = viewer.scene.add(geometry)
    obj = viewer.scene.render_object(sceneobject)

    point_positions, _, point_indices = obj._read_points_data()
    edge_positions, _, edge_indices = obj._read_lines_data()
    face_positions, _, face_indices = obj._read_frontfaces_data()
    _, _, backface_indices = obj._read_backfaces_data()

    assert point_positions is geometry.vertices
    assert edge_positions is geometry.vertices
    assert face_positions is geometry.vertices
    np.testing.assert_array_equal(point_indices, [0, 3])
    np.testing.assert_array_equal(edge_indices, [[0, 1], [2, 3]])
    np.testing.assert_array_equal(face_indices, [[0, 1, 2], [1, 3, 2]])
    np.testing.assert_array_equal(backface_indices, [[0, 2, 1], [1, 2, 3]])


def test_large_indexed_geometry_keeps_one_shared_vertex_table(viewer):
    count = 10_000
    vertices = np.zeros((count, 3), dtype=np.float32)
    edges = np.column_stack((np.arange(count - 1), np.arange(1, count)))
    triangles = np.column_stack((np.zeros(count - 2, dtype=int), np.arange(1, count - 1), np.arange(2, count)))
    geometry = BufferGeometry(vertices, edges=edges, triangles=triangles)
    sceneobject = viewer.scene.add(geometry)
    obj = viewer.scene.render_object(sceneobject)

    assert len(viewer.scene.objects) == 1
    assert obj._read_lines_data()[0].shape == (count, 3)
    assert obj._read_lines_data()[2].size == 2 * (count - 1)
    assert obj._read_frontfaces_data()[0].shape == (count, 3)
    assert obj._read_frontfaces_data()[2].size == 3 * (count - 2)
