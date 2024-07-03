import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas_viewer.components import Treeform


viewer = Viewer()

mesh = Mesh.from_off(compas.get("tubemesh.off"))
obj = viewer.scene.add(mesh, show_points=True)

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



treeform = Treeform()
viewer.ui.sidebar.widget.addWidget(treeform)

def update_treeform(obj):
    treeform.update_from_dict({"name": obj.name, "objtype": obj.__class__, "item": obj.item, "settings": obj.settings})

viewer.ui.sidebar.sceneform.callback = update_treeform

viewer.show()
