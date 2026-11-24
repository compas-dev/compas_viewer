from random import Random

from compas.colors import Color
from compas.geometry import Point
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

for _ in range(10):
    point = Point(rng.random() * 10, rng.random() * 10, rng.random() * 10)
    viewer.scene.add(
        point,
        pointcolor=Color(rng.random(), rng.random(), rng.random()),
        pointsize=rng.random() * 50,
    )


viewer.show()
