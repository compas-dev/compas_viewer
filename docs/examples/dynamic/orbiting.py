from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Frame
from compas.geometry import Sphere
from compas_viewer import Viewer

sphere = Sphere(1.0, Frame.worldXY())

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer(show_grid=False, rendermode="lighted")
viewer.renderer.camera.rotation.x = 10
viewer.renderer.camera.rotation.y = 10
viewer.renderer.camera.distance = 5

viewer.scene.add(
    Mesh.from_shape(sphere, u=32, v=32),
    facecolor=Color.cyan(),
    edgecolor=Color.blue(),
    use_vertexcolors=False,
)


@viewer.on(interval=100)
def orbit(f):
    viewer.renderer.camera.rotation.z += 1


viewer.show()
