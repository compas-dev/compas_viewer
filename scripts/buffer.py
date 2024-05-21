from compas_viewer.scene import BufferGeometry
from compas_viewer import Viewer
import numpy as np


points = np.random.rand(1000, 3) * 10
pointcolor = np.random.rand(1000, 4)

lines = np.random.rand(1000 * 6, 3) * 10
linecolor = np.random.rand(1000 * 6, 4)

faces = np.random.rand(1000 * 9, 3) * 10
facecolor = np.random.rand(1000 * 9, 4)

geometry = BufferGeometry(points=points, pointcolor=pointcolor, lines=lines, linecolor=linecolor, faces=faces, facecolor=facecolor)

viewer = Viewer()
viewer.scene.add(geometry)
viewer.show()