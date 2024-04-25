from math import cos, radians, sin
from random import random

from compas.colors import Color
from compas.geometry import Vector
from compas_viewer import Viewer

viewer = Viewer()

for i in range(0, 360, 20):
    for j in range(0, 180, 10):
        position = Vector(
            sin(radians(i)) * sin(radians(j)),
            cos(radians(i)) * sin(radians(j)),
            cos(radians(j)),
        )
        vector = Vector(sin(radians(i)), cos(radians(i)), cos(radians(j)))
        viewer.scene.add(vector, anchor=position, linecolor=Color(random(), random(), random()))

viewer.show()
