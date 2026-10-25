from compas.colors import Color
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.scene import TextAnnotation

viewer = Viewer()

t = TextAnnotation("a", (0, 0, 0), height=50)
viewer.scene.add(t)

t = TextAnnotation("123", (0, 0, 0), height=50)
t.transform(Translation.from_vector([3, 0, 0]))
viewer.scene.add(t)

t = TextAnnotation(
    "ABC\nWorld-space annotation",
    (0, 0, 0),
    height=0.25,
    absolute_height=True,
    color=Color.red(),
    backgroundcolor=Color(1, 1, 1, 0.85),
    padding=0.04,
    offset=(0, 0.1),
)
t_obj = viewer.scene.add(t)
t_obj.transformation = Translation.from_vector([3, 3, 0])


viewer.show()
