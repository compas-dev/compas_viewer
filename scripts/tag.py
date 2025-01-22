from compas_viewer import Viewer
from compas_viewer.scene import Tag

t1 = Tag("Align to left", (0, 0, 0), height=50) # default align is left and bottom
t2 = Tag("Align to center", (0, 5, 0), height=50, horizontal_align="center", vertical_align="center")
t3 = Tag("Align to right", (0, 10, 0), height=50, horizontal_align="right", vertical_align="top")
t4 = Tag("Absolute height", (5, 0, 0), absolute_height=True, height=100)

viewer = Viewer()
viewer.scene.add([t1, t2, t3, t4])
viewer.show()
