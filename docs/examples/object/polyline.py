import random

from compas.colors import Color
from compas.geometry import Polyline

from compas_viewer import Viewer

viewer = Viewer()

pts = []
for i in range(10):
    pts.append([random.uniform(0, 10), random.uniform(0, 10), random.uniform(0, 10)])

polyline = Polyline(pts)
viewer.scene.add(polyline, show_points=True, pointcolor=Color(1.0, 0.0, 1.0), linecolor=Color(1.0, 0.5, 1.0), lineswidth=1)

pts = []
for i in range(5):
    pts.append([random.uniform(0, 10), random.uniform(0, 10), random.uniform(0, 10)])

polyline = Polyline(pts)
viewer.scene.add(polyline, show_points=True, pointcolor=Color(0.0, 0.0, 1.0), linecolor=Color(1.0, 0.0, 0.0), lineswidth=5)

viewer.show()
