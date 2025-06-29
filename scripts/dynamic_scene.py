from compas.geometry import Box
from compas_viewer import Viewer
from compas.colors import Color

viewer = Viewer()

boxes = [
    Box.from_width_height_depth(1, 1, 1),
    Box.from_width_height_depth(2, 2, 0.5),
    Box.from_width_height_depth(3, 3, 0.2),
]

obj1 = viewer.scene.add(boxes[0], facecolor=Color.blue())

objects_to_remove = [obj1]


@viewer.on(interval=1000)
def dynamic_update(frame):
    """
    This function is called every 1000ms for 6 frames.
    """
    print(f"Frame {frame}")

    if frame == 1:
        print("Adding second box...")
        added_object = viewer.scene.add(boxes[1], facecolor=Color.red())
        objects_to_remove.append(added_object)

    if frame == 2:
        print("Adding third box...")
        added_object = viewer.scene.add(boxes[2], facecolor=Color.green())
        objects_to_remove.append(added_object)

    if frame == 4:
        print("Removing first box...")
        viewer.scene.remove(objects_to_remove.pop(-1))

    if frame == 5:
        print("Removing second box...")
        viewer.scene.remove(objects_to_remove.pop(-1))

    if frame == 6:
        print("Removing third box...")
        viewer.scene.remove(objects_to_remove.pop(-1))

viewer.show()
