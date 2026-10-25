from compas_viewer.components import Sceneform
from compas_viewer.components import SceneTree
from compas_viewer.config import SidebarConfig
from compas_viewer.uidefinitions import default_sidebar_items


def test_sidebar_is_visible_with_scene_tree_by_default():
    config = SidebarConfig()
    items = default_sidebar_items()

    assert config.show
    assert config.width >= config.minimum_width
    assert items[0]["type"] == "SceneTree"
    assert [column["title"] for column in items[0]["columns"]] == ["Name", "Type", "Show"]


def test_scene_tree_preserves_sceneform_compatibility():
    assert issubclass(SceneTree, Sceneform)
