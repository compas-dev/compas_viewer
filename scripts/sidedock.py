from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.components import Button

viewer = Viewer()

box = Box(1, 1, 1)
boxobj = viewer.scene.add(box)


def toggle_box():
    boxobj.show = not boxobj.show
    viewer.renderer.update()


viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Button(text="Toggle Box", action=toggle_box))
viewer.show()
