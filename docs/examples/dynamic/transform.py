from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Scale
from compas.geometry import Translation

from compas_viewer import Viewer

viewer = Viewer()

box1 = Box(1, 1, 1, Frame([0, 0, 0], [1, 0, 0], [0, 1, 0]))
box2 = Box(1, 1, 1, Frame([0, 0, 0], [1, 0, 0], [0, 1, 0]))
box3 = Box(1, 1, 1, Frame([0, 0, 0], [1, 0, 0], [0, 1, 0]))
obj1 = viewer.add(box1, facescolor=Color.red())
obj2 = viewer.add(box2, facescolor=Color.blue())
obj3 = viewer.add(box3, facescolor=Color.green())

s = 1


@viewer.on(interval=100)
def transform(frame):
    obj1.transformation = Translation.from_vector([0, 0, 0.01 * frame])
    obj1.update()

    obj2.transformation = Translation.from_vector([0, 0.01 * frame, 0])
    obj2.update()

    S = Scale.from_factors([0.01 * frame, 0.01 * frame, 0.01 * frame])
    obj3.transformation = S
    obj3.update()


viewer.show()
