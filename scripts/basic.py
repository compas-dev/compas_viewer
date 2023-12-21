from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.scene import BoxObject

viewer = Viewer()
obj = BoxObject(Box.from_width_height_depth(1, 1, 1))
viewer.render.objects[obj] = obj
viewer.show()
