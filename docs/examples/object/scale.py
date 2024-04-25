from compas.geometry import Torus

from compas_viewer import Viewer

viewer = Viewer(rendermode="lighted")

for i in range(1, 1000, 100):
    viewer.scene.add(Torus(i, i / 10), u=int(i / 5) + 10)

viewer.show()
