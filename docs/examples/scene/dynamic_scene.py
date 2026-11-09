from compas.colors import Color
from compas.geometry import Box
from compas_viewer import Viewer

viewer = Viewer()

boxes = [
    Box(1, 1, 1),
    Box(2, 2, 0.5),
    Box(3, 3, 0.2),
]

first_object = viewer.scene.add(boxes[0], surfacecolor=Color.blue())

objects_to_remove = [first_object]


@viewer.on(interval=1000)
def dynamic_update(frame: int) -> None:
    """Update the scene once per second for six frames."""
    print(f"Frame {frame}")

    if frame == 1:
        print("Adding second box...")
        added_object = viewer.scene.add(boxes[1], surfacecolor=Color.red())
        objects_to_remove.append(added_object)

    if frame == 2:
        print("Adding third box...")
        added_object = viewer.scene.add(boxes[2], surfacecolor=Color.green())
        objects_to_remove.append(added_object)

    if frame == 4:
        print("Removing first box...")
        viewer.scene.remove(objects_to_remove.pop(0))

    if frame == 5:
        print("Removing second box...")
        viewer.scene.remove(objects_to_remove.pop(0))

    if frame == 6:
        print("Removing third box...")
        viewer.scene.remove(objects_to_remove.pop(0))


viewer.show()
