from random import random

from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Line
from compas_viewer.scene import Collection
from compas_viewer.viewer import Viewer

viewer = Viewer()

boxes = []
for i in range(5):
    for j in range(5):
        box = Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0]))
        boxes.append(box)

viewer.scene.add(Collection(boxes), name="Boxes")

lines = []
for _ in range(50):
    lines.append(Line([random() * 5, random() * 5, random() * 5], [random() * 5, random() * 5, random() * 5]))

viewer.scene.add(Collection(lines), name="Lines")

viewer.show()
