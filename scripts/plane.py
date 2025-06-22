from compas.geometry import Plane
from compas_viewer import Viewer

viewer = Viewer()

plane = Plane([0, 0, 1], [0, 1, 1])

viewer.scene.add(plane, show_points=True)
viewer.show()