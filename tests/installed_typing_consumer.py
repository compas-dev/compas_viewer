from compas.data import Data
from compas.scene import SceneObject
from compas.typing import PointLike
from compas_viewer.renderer import Camera
from compas_viewer.scene import ViewerScene


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
