from compas.geometry import Polygon
from compas_viewer.viewer import Viewer

viewer = Viewer()
polygon = Polygon([[0, 0, 0], [0.5, 0.5, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
viewer.scene.add(polygon)
viewer.show()
