import compas
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer

viewer = Viewer()

mesh = Mesh.from_off(compas.get("tubemesh.off"))
obj = viewer.scene.add(mesh)

for i in range(5):
    for j in range(5):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            name=f"Box_{i}_{j}",
        )

viewer.show()
