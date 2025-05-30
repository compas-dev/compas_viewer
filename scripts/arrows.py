from compas.colors import Color
from compas.geometry import Vector
from compas_viewer.viewer import Viewer

viewer = Viewer()

N = 10
M = 10

for i in range(N):
    for j in range(M):
        viewer.scene.add(
            Vector(0, 0, (i + j + 1) / 5),
            anchor = [i, j, 0],
            linecolor=Color(i / N, j / M, 0.0),
            name=f"Arrow_{i}_{j}",
        )

viewer.show()
