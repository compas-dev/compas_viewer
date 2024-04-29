from compas.geometry import Frame
from compas_viewer import Viewer

viewer = Viewer()

frame = Frame([1, 1, 1], [0.68, 0.68, 0.27], [-0.67, 0.73, -0.15])

viewer.scene.add(frame)

viewer.show()
