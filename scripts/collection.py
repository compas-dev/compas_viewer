from compas.geometry import Box
from compas.geometry import Line
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas_viewer.scene import Collection
from random import random

viewer = Viewer()

boxes = []
for i in range(20):
    for j in range(20):
        box = Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0]))
        boxes.append(box)

viewer.scene.add(Collection(boxes), name="Boxes")

lines = []
for i in range(1000):
    lines.append(Line([random() * 20, random() * 20, random() * 20], [random() * 20, random() * 20, random() * 20]))

viewer.scene.add(Collection(lines), name="Lines")

viewer.show()
