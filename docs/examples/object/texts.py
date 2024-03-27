from compas.colors import Color
from compas.geometry import Translation

from compas_viewer import Viewer
from compas_viewer.scene import Tag

viewer = Viewer()


texts = """

COMPAS:
The computational
framework
for research
and collaboration
in Architecture,
Engineering,
Fabrication,
and Construction

"""


t = Tag(
    texts,
    (0, 0, 0),
    height=100,
)
viewer.scene.add(t)

t = Tag("123", (0, 0, 0), height=50)
t.transform(Translation.from_vector([3, 0, 0]))
viewer.scene.add(t)

t = Tag("ABC", (0, 0, 0), height=10, absolute_height=True, color=Color.red())
t_obj = viewer.scene.add(t)
t_obj.transformation = Translation.from_vector([3, 3, 0])


viewer.show()
