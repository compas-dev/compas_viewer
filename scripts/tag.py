
from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.scene import Tag

box1 = Box.from_width_height_depth(5, 1, 1)
box2 = Box.from_width_height_depth(1, 5, 1)
t = Tag("EN", (5, 1, 1), height=50)
viewer = Viewer()

# Simple list of objects
group1 = viewer.scene.add([box1, box2, t])
viewer.show()
