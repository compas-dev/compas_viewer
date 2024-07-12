from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas_viewer.config import Config

config = Config()
config.unit = "mm"
viewer = Viewer(config)

for i in range(10):
    for j in range(10):
        viewer.scene.add(
            Box(500, 500, 500, Frame([i * 1000, j * 1000, 0], [1, 0, 0], [0, 1, 0])),
            show_lines=True,
            surfacecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

viewer.show()
