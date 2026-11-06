from compas.colors import Color
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
    sphere.to_polygonal_surface(nu=32, nv=32).to_mesh(),
    facecolor=Color.cyan(),
    linecolor=Color.blue(),
    use_vertexcolors=False,
)


@viewer.on(interval=100)
def orbit(f):
    viewer.renderer.camera.rotation.z += 0.02


viewer.show()
