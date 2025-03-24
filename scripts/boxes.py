from compas.colors import Color
from compas.geometry import Box
from compas_viewer.viewer import Viewer
from compas.geometry import Translation

viewer = Viewer()
N = 10
for i in range(N):
    for j in range(N):
        for k in range(N):
            obj = viewer.scene.add(
                Box(0.5, 0.5, 0.5),
                show_points=True,
                linecolor=Color.white(),
                pointcolor=Color(1 - i / N, 1 - j / N, 1 - k / N),
                pointsize=10,
                facecolor=Color(i / N, j / N, k / N),
                name=f"Box_{i}_{j}_{k}",
            )

            obj.transformation = Translation.from_vector([i, j, k])

viewer.show()
