import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer.viewer import Viewer

viewer = Viewer(show_grid=True)


X = 1
Y = 1
Z = 1

box = Box(0.5, 0.5, 0.5)

for i in range(X):
    for j in range(Y):
        for k in range(Z):
            obj = viewer.scene.add(
                box,
                linecolor=Color.white(),
                facecolor=Color(i / X, j / Y, k / Z),
                name=f"Box_{i}_{j}_{k}",
            )
            obj.transformation = Translation.from_vector([i, j, k])


viewer.show()
