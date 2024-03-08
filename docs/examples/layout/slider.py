from compas.colors import Color
from compas.geometry import Bezier
from compas.geometry import Point
from compas.geometry import Polyline

from compas_viewer import Viewer
from compas_viewer.layout import Slider
from compas_viewer.scene import PointObject

curve = Bezier([[0, 0, 0], [3, 6, 0], [5, -3, 0], [10, 0, 0]])

viewer = Viewer(rendermode="shaded", width=1600, height=900)


pointobj: PointObject = viewer.scene.add(Point(*curve.point_at(0)), pointssize=20, pointcolor=Color.red(), show_points=True)  # type: ignore
curveobj = viewer.scene.add(Polyline(curve.to_polyline()), lineswidth=2, linecolor=Color.blue())


def slide(value, additional_var):
    value = value / 100
    print(additional_var + str(value))
    pointobj.geometry = curve.point_at(value)
    pointobj.init()
    pointobj.update()
    viewer.renderer.update()


viewer.layout.sidedock.add_element(
    Slider(slide, 0, 0, 100, 1, "Slide Point", additional_var="Slide the point along the curve at ")
)


viewer.show()
