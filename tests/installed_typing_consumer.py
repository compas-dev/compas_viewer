from compas.data import Data
from compas.typing import PointLike
from compas_viewer.renderer import Camera
from compas_viewer.scene import ViewerScene
from compas_viewer.scene import ViewerSceneObject


def consume_viewer_types(
    scene: ViewerScene,
    item: Data,
    sceneobject: ViewerSceneObject,
    point: PointLike,
) -> None:
    added: ViewerSceneObject = scene.add(item)
    preserved: ViewerSceneObject = scene.add(sceneobject)
    camera = Camera.__new__(Camera)
    camera.position = point
    camera.target = point

    assert added is not preserved
