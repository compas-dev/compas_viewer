from compas.geometry import Frame
from compas.geometry import Sphere

from compas_viewer import Viewer
from compas_viewer.layout import Treeform

viewer = Viewer(rendermode="shaded")

viewer = Viewer()
for i in range(10):
    for j in range(10):
        sp = viewer.scene.add(Sphere(1, Frame([10 * i, 10 * j, 0], [1, 0, 0], [0, 1, 0])), name=f"Sphere_{i}_{j}")


viewer.layout.sidedock.add_element(Treeform(viewer.scene, {"Name": (lambda o: o.name), "Object": (lambda o: o)}))


viewer.show()
