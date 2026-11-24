from compas.geometry import Torus
from compas_viewer import Viewer
from compas_viewer.config import Config

config = Config()
config.renderer.rendermode = "lighted"

viewer = Viewer(config=config)

for i in range(1, 1000, 100):
    viewer.scene.add(Torus(i, i / 10), u=int(i / 5) + 10)

viewer.show()
