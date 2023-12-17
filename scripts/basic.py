from compas_viewer import Viewer
from compas.geometry import Sphere

viewer = Viewer()
viewer.add(Sphere([0, 0, 0], 1))
viewer.run()
