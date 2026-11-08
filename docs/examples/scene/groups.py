from compas.geometry import Box
from compas.scene import TextAnnotation
from compas_viewer import Viewer

viewer = Viewer()

group = viewer.scene.add_group(name="Cross")
group.add(Box(5, 1, 1), name="Horizontal")
group.add(Box(1, 5, 1), name="Vertical")
group.add(TextAnnotation("Grouped objects", (3, 0, 0), height=32), name="Label")
viewer.show()
