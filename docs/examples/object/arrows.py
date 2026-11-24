from random import Random

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Vector
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

for x in range(5):
    for y in range(5):
        viewer.scene.add(Vector(0, 0, 1), anchor=Point(x, y, 0), linecolor=Color.from_i(rng.random()))

viewer.show()
