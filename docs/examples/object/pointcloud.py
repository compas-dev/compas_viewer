from random import Random

from compas.colors import Color
from compas.geometry import Pointcloud
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)
points = [[rng.uniform(0, 10), rng.uniform(0, 10), rng.uniform(0, 10)] for _ in range(1000)]
pointcloud = Pointcloud(points)
viewer.scene.add(pointcloud, pointcolor=Color(1.0, 0.0, 0.0), pointsize=10)

viewer.show()
