import numpy as np

from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.scene import BufferGeometry

vertices = np.array(
    [
        [0.0, 0.0, 0.0],
        [2.0, 0.0, 0.0],
        [2.0, 2.0, 0.0],
        [0.0, 2.0, 0.0],
    ],
    dtype=np.float32,
)
edges = np.array([[0, 1], [1, 2], [2, 3], [3, 0]], dtype=np.int32)
triangles = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)

linecolor = np.tile([0.1, 0.4, 0.9, 1.0], (len(vertices), 1))
facecolor = np.tile([0.9, 0.4, 0.1, 1.0], (len(vertices), 1))

edge_geometry = BufferGeometry.from_vertices_and_edges(vertices, edges, linecolor=linecolor)
triangle_geometry = BufferGeometry.from_vertices_and_triangles(vertices, triangles, facecolor=facecolor)

viewer = Viewer()
viewer.scene.add(edge_geometry, name="Indexed edges")
viewer.scene.add(
    triangle_geometry,
    name="Indexed triangles",
    transformation=Translation.from_vector([3.0, 0.0, 0.0]),
)
viewer.show()
