from random import random

from compas.colors import Color
from compas.geometry import Line

from compas_viewer import Viewer

viewer = Viewer()

for i in range(10):
    line = Line([random() * 20, random() * 20, random() * 20], [random() * 20, random() * 20, random() * 20])
    viewer.scene.add(line, linescolor=Color(random(), random(), random()))

viewer.show()
