from compas.geometry import Box
from compas.geometry import Brep
from compas.geometry import Frame
from compas_viewer import Viewer

box = Box(1, 1, 1, Frame.worldXY())
brep = Brep.from_box(box)

viewer = Viewer()
viewer.scene.add(brep)
viewer.show()
