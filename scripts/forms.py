import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas_viewer.config import Config
from compas_viewer.components import Sceneform

config = Config()
config.ui.sidebar.sceneform = False
config.ui.sidedock.show = False

viewer = Viewer(config=config)

mesh = Mesh.from_off(compas.get("tubemesh.off"))
obj = viewer.scene.add(mesh, show_points=True, facecolor=Color.blue(), linecolor=Color.red(), pointcolor=Color.green())

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


def callback(item):
    print("Callback triggered on", item)

viewer.ui.sidebar.widget.addWidget(Sceneform(viewer.scene, {"Name": (lambda o: o.name)}, callback=callback))

viewer.show()
