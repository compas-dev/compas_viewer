from random import random

from compas.colors import Color
from compas.geometry import Point
from compas_viewer import Viewer

viewer = Viewer()
for i in range(10):
    point = Point(random() * 10, random() * 10, random() * 10)
    viewer.scene.add(point, pointcolor=Color(random(), random(), random()), pointsize=random() * 50)


viewer.show()
