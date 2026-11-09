from random import Random

from compas.colors import Color
from compas.geometry import Line
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

for _ in range(10):
    line = Line(
        [rng.random() * 20, rng.random() * 20, rng.random() * 20],
        [rng.random() * 20, rng.random() * 20, rng.random() * 20],
    )
    viewer.scene.add(line, linecolor=Color(rng.random(), rng.random(), rng.random()))

viewer.show()
