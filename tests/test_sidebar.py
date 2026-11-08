from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

from compas.geometry import Sphere
from compas_viewer.components import Sceneform
from compas_viewer.components import SceneTree
from compas_viewer.config import Config
from compas_viewer.config import SidebarConfig
from compas_viewer.scene import ViewerScene
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_sidebar_items


def test_sidebar_is_visible_with_scene_tree_by_default():
    config = SidebarConfig()
    items = default_sidebar_items()

    assert config.show
    assert config.width >= config.minimum_width
    assert items[0]["type"] == "SceneTree"
    assert items[2]["type"] == "DatastructureAttributes"
    assert [column["title"] for column in items[0]["columns"]] == ["Name", "Type", "Show"]


def test_scene_tree_preserves_sceneform_compatibility():
    assert issubclass(SceneTree, Sceneform)


def test_scene_tree_replaces_selection_in_scene_order(monkeypatch):
    app = QApplication.instance() or QApplication([])
    scene = ViewerScene()
    first = scene.add(Sphere(1.0), name="First")
    second = scene.add(Sphere(2.0), name="Second")
    state = ViewerState(Config(), scene.object)
    viewer = SimpleNamespace(scene=scene, state=state)
    monkeypatch.setattr(Sceneform, "viewer", property(lambda _self: viewer), raising=False)
    tree = Sceneform(columns=[{"title": "Name", "type": "label", "text": lambda obj: obj.name}])
    tree.update()
    changes = []
    state.changed.connect(lambda path, value: changes.append((path, value)))

    tree.widget.blockSignals(True)
    tree._widgets[second.guid].setSelected(True)
    tree._widgets[first.guid].setSelected(True)
    tree.widget.blockSignals(False)
    tree._sync_selection_from_widget()

    assert state.selection.objects == (first, second)
    assert changes == [("selection", (first.guid, second.guid))]
    assert app is not None
