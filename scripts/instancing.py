import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer

viewer = Viewer(show_grid=True)


N = 10
M = 10

box = Box(0.5, 0.5, 0.5)

viewer.scene.add(box)
viewer.scene.add(box)


viewer.show()
