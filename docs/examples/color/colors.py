from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()

box = Box(1, 1, 1, Frame((0, 0, 0), [1, 0, 0], [0, 1, 0]))
obj1 = viewer.scene.add(box, surfacecolor=Color(1.0, 0.0, 0.0), opacity=0.7)

box = Box(1, 1, 1, Frame((0, 0, 0), [1, 0, 0], [0, 1, 0]))
obj2 = viewer.scene.add(box, surfacecolor=Color(0.0, 1.0, 0.0), opacity=0.7)

box = Box(1, 1, 1, Frame((0, 0, 0), [1, 0, 0], [0, 1, 0]))
obj3 = viewer.scene.add(box, surfacecolor=Color(0.0, 0.0, 1.0), opacity=0.7)


obj2.transformation = Translation.from_vector([2, 0, 0])
obj3.transformation = Translation.from_vector([4, 0, 0])

viewer.show()
