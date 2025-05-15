from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.scene import Tag

box1 = Box.from_width_height_depth(5, 1, 1)
box2 = Box.from_width_height_depth(1, 5, 1)
t = Tag("EN", (5, 0, 0), height=50)


viewer = Viewer()

# Just fix API for groups
group1 = viewer.scene.add_group(name="group1")
group1.add(box1, name="box1")
group1.add(box2, name="box2")
group1.add(t, name="tag")
viewer.show()
