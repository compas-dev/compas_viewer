from compas.geometry import Frame
from compas.geometry import Sphere
from compas_viewer import Viewer
from compas_viewer.components import SceneTree

viewer = Viewer()
for i in range(10):
    for j in range(10):
        viewer.scene.add(Sphere(1, Frame([10 * i, 10 * j, 0], [1, 0, 0], [0, 1, 0])), name=f"Sphere_{i}_{j}")

viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(SceneTree(columns=[{"title": "Name", "type": "label", "text": lambda node: node.name}]))

viewer.show()
