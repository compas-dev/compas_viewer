from compas.colors import Color
from compas.geometry import Bezier
from compas_viewer import Viewer
from compas_viewer.components import Component
from compas_viewer.components import Slider

curve = Bezier([[0, 0, 0], [3, 6, 0], [5, -3, 0], [10, 0, 0]])

viewer = Viewer()

point = curve.point_at(0)
pointobj = viewer.scene.add(point, pointsize=20, pointcolor=Color.red(), show_points=True)
viewer.scene.add(curve.to_polyline(), linewidth=2, linecolor=Color.blue(), show_points=False)


def slide(_component: Component, value: float) -> None:
    sample = curve.point_at(value)
    point.x = sample.x
    point.y = sample.y
    point.z = sample.z
    pointobj.refresh_data()
    pointobj.update(update_data=True)
    viewer.renderer.update()


viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Slider(value=0, min_val=0, max_val=1, step=0.01, title="Slide Point", action=slide))

viewer.show()
