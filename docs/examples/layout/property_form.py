from compas.geometry import Box
from compas.geometry import Frame

from compas_viewer import Viewer
from compas_viewer.layout import Propertyform

viewer = Viewer(rendermode="shaded")


box_obj = viewer.scene.add(Box(5, 5, 5, Frame.worldXY()), name=f"Sphere")


viewer.layout.sidedock.add_element(Propertyform(box_obj))


viewer.show()
