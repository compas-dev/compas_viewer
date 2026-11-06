from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer import Viewer
from compas_viewer.components import SceneTree

viewer = Viewer()

for i in range(10):
    for j in range(10):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            show_points=False,
            show_lines=True,
            surfacecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(SceneTree(columns=[{"title": "Name", "type": "label", "text": lambda node: node.name}]))

viewer.show()
