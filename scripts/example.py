import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer

viewer = Viewer(show_grid=True)

mesh = Mesh.from_off(compas.get("tubemesh.off"))
obj = viewer.scene.add(mesh, show_points=True, facecolor=Color.blue(), linecolor=Color.red(), pointcolor=Color.green())

for i in range(5):
    for j in range(5):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            linecolor=Color.white(),
            facecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

viewer.show()
