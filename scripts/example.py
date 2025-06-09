import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from random import random
from compas_viewer.viewer import Viewer

viewer = Viewer(show_grid=True)

mesh = Mesh.from_off(compas.get("tubemesh.off"))
obj = viewer.scene.add(mesh, show_points=True)

N = 10
M = 10

for i in range(N):
    for j in range(M):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            linecolor=Color.from_i(random()),
            facecolor=Color(i / N, j / M, 0.0),
            name=f"Box_{i}_{j}",
            linewidth=3 * random(),
            show_points=True,
            pointcolor=Color.from_i(random()),
            pointsize=10
        )

viewer.show()
