from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas_viewer.components import Button
from compas_viewer.components import Slider

viewer = Viewer()

viewer.renderer.camera.target = [5, 0, 0]
viewer.renderer.camera.position = [5, 10, 5]

print("target", viewer.renderer.camera.target)

for i in range(5):
    for j in range(5):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            show_points=True,
            show_lines=True,
            surfacecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

def print_camera():
    print("target", viewer.renderer.camera.target)
    print("position", viewer.renderer.camera.position)


def update_camera_position_x(slider: Slider, value: int):
    viewer.renderer.camera.position.x = value
    viewer.renderer.update()
    print(viewer.renderer.camera.position)

def update_camera_position_y(slider: Slider, value: int):
    viewer.renderer.camera.position.y = value
    viewer.renderer.update()
    print(viewer.renderer.camera.position)


def update_camera_position_z(slider: Slider, value: int):
    viewer.renderer.camera.position.z = value
    viewer.renderer.update()
    print(viewer.renderer.camera.position)


def update_camera_target_x(slider: Slider, value: int):
    viewer.renderer.camera.target.x = value
    viewer.renderer.update()
    print(viewer.renderer.camera.target)
    

def update_camera_target_y(slider: Slider, value: int):
    viewer.renderer.camera.target.y = value
    viewer.renderer.update()
    print(viewer.renderer.camera.target)

def update_camera_target_z(slider: Slider, value: int):
    viewer.renderer.camera.target.z = value
    viewer.renderer.update()
    print(viewer.renderer.camera.target)


viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Button(text="Print Camera", action=print_camera))
viewer.ui.sidedock.add(Slider(title="Position X", min_val=-10, max_val=10, step=1, action=update_camera_position_x))
viewer.ui.sidedock.add(Slider(title="Position Y", min_val=-10, max_val=10, step=1, action=update_camera_position_y))
viewer.ui.sidedock.add(Slider(title="Position Z", min_val=-10, max_val=10, step=1, action=update_camera_position_z))
viewer.ui.sidedock.add(Slider(title="Target X", min_val=-10, max_val=10, step=1, action=update_camera_target_x))
viewer.ui.sidedock.add(Slider(title="Target Y", min_val=-10, max_val=10, step=1, action=update_camera_target_y))
viewer.ui.sidedock.add(Slider(title="Target Z", min_val=-10, max_val=10, step=1, action=update_camera_target_z))

viewer.show()
