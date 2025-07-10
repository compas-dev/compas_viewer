from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.components import Button
from compas_viewer.components import Slider

box = Box(1)

viewer = Viewer()

boxobj = viewer.scene.add(box)

import time


def toggle_box():
    boxobj.show = not boxobj.show
    viewer.renderer.update()


def slider_changed1(slider: Slider, value: float):
    global viewer
    global boxobj

    boxobj.transformation = Translation.from_vector([5 * value, 0, 0])
    boxobj.update()
    viewer.renderer.update()

def slider_changed2(slider: Slider, value: float):
    global boxobj

    boxobj.update()
    viewer.renderer.update()

viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Button(text="Toggle Box", action=toggle_box))
viewer.ui.sidedock.add(Slider(title="Move Box", min_val=0, max_val=2, step=0.2, action=slider_changed1))
viewer.ui.sidedock.add(Slider(title="Box Opacity", obj=boxobj, attr="opacity", min_val=0, max_val=1, step=0.1, action=slider_changed2))

viewer.show()
