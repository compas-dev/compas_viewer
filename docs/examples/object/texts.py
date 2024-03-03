from compas_viewer.scene import Tag

from compas_viewer import Viewer

viewer = Viewer()

t = Tag("a", (0, 0, 0), height=50)
viewer.add(t)

t = Tag("123", (3, 0, 0), height=50)
viewer.add(t)

t = Tag("ABC", (3, 3, 0), height=20, absolute_height=True)
viewer.add(t, color=(1, 0, 0))

viewer.show()
