from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer import Viewer
from compas_viewer.components import Button
from compas_viewer.components import ParameterForm

viewer = Viewer()

box = Box(5, 5, 5)
viewer.scene.add(box, name="Box_1")
viewer.scene.add(Box(5, 5, 5, frame=Frame([-10, -10, 0], [1, 0, 0], [0, 1, 0])), name="Box_2")


def edit_box() -> None:
    ParameterForm(box, title="Edit Box").exec()


viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Button(text="Edit Box", action=edit_box))

viewer.show()
