from compas.data import Data
from compas.scene import SceneObject
from compas.scene import ShapeObject
from compas.typing import PointLike
from compas_viewer.forms import register_scene_attribute_contribution
from compas_viewer.forms import scene_editable_attributes
from compas_viewer.renderer import Camera
from compas_viewer.scene import ViewerScene


def update_resolution(sceneobject: ShapeObject, value: object) -> None:
    if not isinstance(value, int):
        raise TypeError("Shape resolution should be an integer.")
    sceneobject.u = value


register_scene_attribute_contribution("Viewer", ShapeObject, "typing.shape", {"u": update_resolution})
shape_updates = scene_editable_attributes("Viewer", ShapeObject())
shape_update = shape_updates["u"]
if shape_update is not None:
    shape_update(ShapeObject(), 16)


def consume_viewer_types(
    scene: ViewerScene,
    item: Data,
    sceneobject: SceneObject,
    point: PointLike,
) -> None:
    added: SceneObject = scene.add(item)
    preserved: SceneObject = scene.add_object(sceneobject)
    camera = Camera.__new__(Camera)
    camera.position = point
    camera.target = point

    assert added is not preserved
