from compas.colors import Color
from compas.geometry import Point
from compas_viewer import Viewer

viewer = Viewer()
point = Point(0, 0, 0)
sceneobject = viewer.scene.add(point, show_points=True, pointcolor=Color.red(), pointsize=10)


@viewer.on(interval=1000)
def move_point(frame: int) -> None:
    print("frame", frame)
    point.x += 0.1
    viewer.refresh_geometry((sceneobject,))


viewer.show()
