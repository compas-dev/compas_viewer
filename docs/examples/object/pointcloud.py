from random import random

from compas.colors import Color
from compas.geometry import Pointcloud
from compas_viewer import Viewer

viewer = Viewer()
pointcloud = Pointcloud.from_bounds(10, 10, 10, 1000)
viewer.scene.add(pointcloud, pointcolor=Color(1.0,0.0,0.0), pointsize=10)

viewer.show()
