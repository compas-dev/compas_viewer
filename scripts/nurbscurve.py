from compas.geometry import NurbsCurve
from compas_viewer.viewer import Viewer

curve = NurbsCurve.from_points([[0, 0, 0], [1, 1, 0], [2, 0, 0], [3, 1, 0], [4, 0, 0]], degree=3)

viewer = Viewer()
viewer.scene.add(curve)
viewer.show()