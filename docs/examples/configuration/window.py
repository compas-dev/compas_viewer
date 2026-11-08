from compas.geometry import Box
from compas_viewer import Viewer
from compas_viewer.config import Config

config = Config()
config.window.title = "Structural Model"
config.window.width = 1200
config.window.height = 800
config.ui.appearance = "dark"
config.ui.statusbar.show = False
config.renderer.view = "ortho"
config.renderer.gridsize = (20.0, 20, 20.0, 20)

viewer = Viewer(config=config)
viewer.scene.add(Box(2.0), name="Design volume")
viewer.show()
