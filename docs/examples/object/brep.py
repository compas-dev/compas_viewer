from compas_occ.brep import OCCBrep
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer import Viewer

box = Box(1, 1, 1, Frame.worldXY())
brep = OCCBrep.from_box(box)

viewer = Viewer()
viewer.add(brep)
viewer.show()
