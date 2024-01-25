from compas.colors import Color
from compas.geometry import Frame
from compas.geometry import Sphere

from compas_viewer import Viewer

sphere = Sphere(1.0, Frame.worldXY())

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer(show_grid=False)
viewer.renderer.camera.rotation.x = 10
viewer.renderer.camera.rotation.y = 10
viewer.renderer.camera.distance = 5

viewer.add(sphere, facescolor=Color.cyan(), linescolor=Color.blue())


@viewer.on(interval=50)
def orbit(f):
    viewer.renderer.camera.rotation.z += 1


viewer.show()
