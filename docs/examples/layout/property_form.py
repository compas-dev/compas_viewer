from compas.geometry import Box
from compas.geometry import Frame

from compas_viewer import Viewer
from compas_viewer.layout import Propertyform

viewer = Viewer(rendermode="shaded")

box_obj = viewer.scene.add(Box(5, 5, 5, Frame.worldXY()), name="Box_1")
box_obj = viewer.add(Box(5, 5, 5, Frame([-10, -10, 0], [1, 0, 0], [0, 1, 0])), name="Box_2")

viewer.layout.sidedock.add_element(Propertyform())

viewer.show()
