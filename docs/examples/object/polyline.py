from random import Random

from compas.colors import Color
from compas.geometry import Polyline
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

points = []
for _ in range(10):
    points.append([rng.uniform(0, 10), rng.uniform(0, 10), rng.uniform(0, 10)])

polyline = Polyline(points)
viewer.scene.add(polyline, show_points=True, pointcolor=Color(1.0, 0.0, 1.0), linecolor=Color(1.0, 0.5, 1.0), linewidth=1)

points = []
for _ in range(5):
    points.append([rng.uniform(0, 10), rng.uniform(0, 10), rng.uniform(0, 10)])

polyline = Polyline(points)
viewer.scene.add(polyline, show_points=True, pointcolor=Color(0.0, 0.0, 1.0), linecolor=Color(1.0, 0.0, 0.0), linewidth=5)

viewer.show()
