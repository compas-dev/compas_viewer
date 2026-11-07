import numpy as np

from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.scene import BufferGeometry

box = Box(1)
surface = box.to_polygonal_surface()
tessellation = surface.triangulated()

points = np.asarray(surface.vertices, dtype=np.float32)
pointcolor = np.tile([1.0, 0.0, 0.0, 1.0], (len(points), 1))

edges = np.asarray(surface.edges, dtype=np.int32)
linecolor = np.tile([0.0, 1.0, 0.0, 1.0], (len(points), 1))

triangles = np.asarray(tessellation.triangles, dtype=np.int32)
facecolor = np.tile([0.0, 0.0, 1.0, 1.0], (len(points), 1))

geometry = BufferGeometry(
    vertices=points,
    points=np.arange(len(points), dtype=np.int32),
    edges=edges,
    triangles=triangles,
    pointcolor=pointcolor,
    linecolor=linecolor,
    facecolor=facecolor,
)

viewer = Viewer()
viewer.scene.add(geometry)
viewer.show()
