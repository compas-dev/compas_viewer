import numpy as np

from compas_viewer import Viewer
from compas_viewer.scene import BufferGeometry

points = np.random.rand(1000, 3) * 10
pointcolor = np.random.rand(1000, 4)

lines = np.random.rand(1000 * 6, 3) * 10
linecolor = np.random.rand(1000 * 6, 4)

faces = np.random.rand(1000 * 9, 3) * 10
facecolor = np.random.rand(1000 * 9, 4)

geometry = BufferGeometry(points=points, pointcolor=pointcolor, lines=lines, linecolor=linecolor, faces=faces, facecolor=facecolor)

viewer = Viewer()
obj = viewer.scene.add(geometry)


@viewer.on(interval=200)
def update(frame):

    geometry.points = np.random.rand(1000, 3) * 10
    geometry.pointcolor = np.random.rand(1000, 4)
    geometry.lines = np.random.rand(1000 * 6, 3) * 10
    geometry.linecolor = np.random.rand(1000 * 6, 4)
    geometry.faces = np.random.rand(1000 * 9, 3) * 10
    geometry.facecolor = np.random.rand(1000 * 9, 4)

    obj.update(update_data=True)


viewer.show()
