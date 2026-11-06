import numpy as np

from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.scene import BufferGeometry

box = Box(1)
surface = box.to_polygonal_surface()
tessellation = surface.triangulated()

points = np.asarray(surface.vertices, dtype=np.float32)
pointcolor = np.tile([1.0, 0.0, 0.0, 1.0], (len(points), 1))

lines = np.asarray([surface.vertices[index] for edge in surface.edges for index in edge], dtype=np.float32)
linecolor = np.tile([0.0, 1.0, 0.0, 1.0], (len(lines), 1))

faces = np.asarray(
    [tessellation.vertices[index] for triangle in tessellation.triangles for index in triangle],
    dtype=np.float32,
)
facecolor = np.tile([0.0, 0.0, 1.0, 1.0], (len(faces), 1))

geometry = BufferGeometry(
    points=points,
    pointcolor=pointcolor,
    lines=lines,
    linecolor=linecolor,
    faces=faces,
    facecolor=facecolor,
)

viewer = Viewer()
viewer.scene.add(geometry)
viewer.show()
