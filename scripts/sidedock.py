from compas_viewer import Viewer
from compas_viewer.components.button import Button

viewer = Viewer()
viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Button("camera_info.svg", "tool tips", lambda: print("do something")))

viewer.show()