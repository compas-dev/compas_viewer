from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.scene import Tag

viewer = Viewer()

group = viewer.scene.add_group(name="Cross")
group.add(Box.from_width_height_depth(5, 1, 1), name="Horizontal")
group.add(Box.from_width_height_depth(1, 5, 1), name="Vertical")
group.add(Tag("Grouped objects", (3, 0, 0), height=32), name="Label")
viewer.show()
