from compas.colors import Color
from compas.geometry import Frame
from compas.geometry import Sphere
from compas_viewer import Viewer
from compas_viewer.config import Config

sphere = Sphere(1.0, Frame.worldXY())

config = Config()
config.renderer.show_grid = False
config.renderer.rendermode = "lighted"

viewer = Viewer(config=config)
viewer.renderer.camera.rotation.x = 10
viewer.renderer.camera.rotation.y = 10
viewer.renderer.camera.distance = 5

viewer.scene.add(
    sphere,
    surfacecolor=Color.cyan(),
    linecolor=Color.blue(),
    u=32,
    v=32,
)


@viewer.on(interval=100)
def orbit(_frame: int) -> None:
    viewer.renderer.camera.rotation.z += 0.02


viewer.show()
