from compas.colors import Color
from compas.geometry import Point

from compas_viewer import Viewer

viewer = Viewer()
obj = viewer.add(Point(0, 0, 0), show_points=True, pointscolor=Color.red(), pointsize=10)


@viewer.on(interval=1000)
def movepoint(frame):
    print("frame", frame)
    obj.geometry.x += 0.1
    obj.init()
    obj.update()


viewer.show()
