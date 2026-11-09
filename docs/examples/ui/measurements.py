from compas.datastructures import Mesh
from compas_viewer import Viewer
from compas_viewer.config import Config

config = Config()
config.measurement.unit = "m"
config.measurement.precision = 2

viewer = Viewer(config=config)

mesh = Mesh.from_vertices_and_faces(
    [
        [0, 0, 0],
        [4, 0, 0],
        [4, 3, 0],
        [0, 3, 0],
    ],
    [[0, 1, 2, 3]],
)
viewer.scene.add(
    mesh,
    name="Measurement target",
    show_vertices=True,
    show_edges=True,
    vertexsize=10,
    edgewidth=2,
)

viewer.start_distance_dimension(mode="fixed")
viewer.show()
