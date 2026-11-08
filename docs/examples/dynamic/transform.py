from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Scale
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()

box = Box(1, 1, 1, Frame.worldXY())
vertical_object = viewer.scene.add(box, surfacecolor=Color.red())
horizontal_object = viewer.scene.add(box.copy(), surfacecolor=Color.blue())
scaled_object = viewer.scene.add(box.copy(), surfacecolor=Color.green())


@viewer.on(interval=100)
def transform_objects(frame: int) -> None:
    vertical_object.transformation = Translation.from_vector([0, 0, 0.01 * frame])
    viewer.scene.render_object(vertical_object).update()

    horizontal_object.transformation = Translation.from_vector([0, 0.01 * frame, 0])
    viewer.scene.render_object(horizontal_object).update()

    scale = Scale.from_factors([0.01 * frame, 0.01 * frame, 0.01 * frame])
    scaled_object.transformation = scale
    viewer.scene.render_object(scaled_object).update()


viewer.show()
