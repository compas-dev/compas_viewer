import numpy as np

from compas_viewer.scene.buffermanager import BufferManager


class BufferedObject:
    def __init__(self, positions, elements, buffer_type="_points_data", object_opacity=1.0, colors=None):
        if colors is None:
            colors = np.ones((np.asarray(positions).size // 3, 4), dtype=np.float32)
        self._points_data = None
        self._lines_data = None
        self._frontfaces_data = None
        self._backfaces_data = None
        setattr(self, buffer_type, (positions, colors, elements))
        self.transformation = None
        self.show = True
        self.show_points = True
        self.show_lines = False
        self.show_faces = False
        self.is_selected = False
        self.opacity = object_opacity
        self.pointsize = 1.0
        self.linewidth = 1.0


def test_buffer_manager_counts_vertices_in_flat_position_arrays():
    manager = BufferManager()
    first = BufferedObject([0, 0, 0, 1, 0, 0], [0, 1])
    second = BufferedObject([[0, 1, 0], [1, 1, 0], [2, 1, 0]], [0, 2])

    manager.add_object(first)
    manager.add_object(second)

    np.testing.assert_array_equal(manager.object_indices["_points_data"], [0, 0, 1, 1, 1])
    np.testing.assert_array_equal(manager.elements["_points_data"], [0, 1, 2, 4])
    assert manager.positions["_points_data"].size == 15


def test_buffer_manager_offsets_indexed_triangles_without_expanding_vertices():
    manager = BufferManager()
    first = BufferedObject([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]], "_frontfaces_data")
    second = BufferedObject([[0, 0, 1], [1, 0, 1], [0, 1, 1]], [[0, 2, 1]], "_frontfaces_data")

    manager.add_object(first)
    manager.add_object(second)

    np.testing.assert_array_equal(manager.elements["_frontfaces_data"], [0, 1, 2, 3, 5, 4])
    np.testing.assert_array_equal(manager.object_indices["_frontfaces_data"], [0, 0, 0, 1, 1, 1])
    assert manager.positions["_frontfaces_data"].size == 18


def test_buffer_manager_partitions_complete_triangles_and_preserves_offsets():
    manager = BufferManager()
    colors = np.ones((4, 4), dtype=np.float32)
    colors[0, 3] = 0.5
    first = BufferedObject(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        [[0, 1, 2], [1, 3, 2]],
        "_frontfaces_data",
        colors=colors,
    )
    second = BufferedObject([[0, 0, 1], [1, 0, 1], [0, 1, 1]], [[0, 2, 1]], "_frontfaces_data")

    manager.add_object(first)
    manager.add_object(second)

    np.testing.assert_array_equal(manager.elements["_frontfaces_data"], [1, 3, 2, 4, 6, 5])
    np.testing.assert_array_equal(manager.elements["_frontfaces_data_transparent"], [0, 1, 2])


def test_buffer_manager_makes_complete_triangles_transparent_with_object_opacity():
    manager = BufferManager()
    obj = BufferedObject(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        [[0, 1, 2], [1, 3, 2]],
        "_frontfaces_data",
        object_opacity=0.5,
    )

    manager.add_object(obj)

    assert manager.elements["_frontfaces_data"].size == 0
    np.testing.assert_array_equal(manager.elements["_frontfaces_data_transparent"], [0, 1, 2, 1, 3, 2])
