from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer

viewer = Viewer()

viewer.renderer.camera.target = [5, 0, 0]
viewer.renderer.camera.position = [5, 10, 5]


for i in range(5):
    for j in range(5):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            show_points=True,
            show_lines=True,
            surfacecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

viewer.show()
