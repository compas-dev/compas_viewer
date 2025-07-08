from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas_viewer.config import Config

config = Config()
for item in config.ui.sidebar.items:
    if item['type'] == 'Sceneform':
        item['area'] = 'tab'
viewer = Viewer(config)

N = 10
M = 10

for i in range(N):
    for j in range(M):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            linecolor=Color.white(),
            facecolor=Color(i / N, j / M, 0.0),
            name=f"Box_{i}_{j}",
        )

viewer.show()
