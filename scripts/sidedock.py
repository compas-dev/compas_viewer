from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.components import Button
from compas_viewer.components import Slider

viewer = Viewer()

box = Box(1, 1, 1)
boxobj = viewer.scene.add(box)


def toggle_box():
    boxobj.show = not boxobj.show
    viewer.renderer.update()

def slider_changed(value):
    print(f"Slider value changed to: {value}")

viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Button(text="Toggle Box", action=toggle_box))
viewer.ui.sidedock.add(Slider(title="test", min_val=0, max_val=10, action=slider_changed))
viewer.show()
