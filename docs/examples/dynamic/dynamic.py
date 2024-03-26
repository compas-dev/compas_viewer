from compas.colors import Color
from compas.geometry import Point

from compas_viewer import Viewer
from compas_viewer.scene import PointObject

viewer = Viewer()
obj: PointObject = viewer.scene.add(Point(0, 0, 0), show_points=True, pointcolor=Color.red(), pointsize=10)  # type: ignore


@viewer.on(interval=1000)
def movepoint(frame):
    print("frame", frame)
    obj.geometry.x += 0.1
    obj.init()
    obj.update()


viewer.show()
