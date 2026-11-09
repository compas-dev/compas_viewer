from types import SimpleNamespace
from typing import Any
from typing import cast
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSplitter

from compas.geometry import Sphere
from compas_viewer.base import Base
from compas_viewer.components import ObjectSetting
from compas_viewer.components import BooleanToggle
from compas_viewer.components import ChoiceEdit
from compas_viewer.components import Container
from compas_viewer.components import NumberEdit
from compas_viewer.components import Sceneform
from compas_viewer.components import SceneTree
from compas_viewer.components import SideBarRight
from compas_viewer.components.systempanel import SystemPanel
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
    assert [item["type"] for item in items] == [
        "SceneTree",
        "AnnotationPanel",
        "ObjectSetting",
        "CameraSetting",
        "DisplaySetting",
        "GridUnitSetting",
    ]
    assert items[-1]["type"] == "GridUnitSetting"
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


def test_sidebar_has_exactly_three_stable_domains_without_splitters(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    viewer = SimpleNamespace(config=config, state=ViewerState(config), sidebar_items=[])
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))

    sidebar = SideBarRight(SimpleNamespace())

    assert [sidebar.widget.tabText(index) for index in range(sidebar.widget.count())] == ["Scene", "Annotations", "System"]
    assert sidebar.widget.currentIndex() == 0
    assert sidebar.widget.findChildren(QSplitter) == []
    assert app is not None


def test_sidebar_navigation_accepts_only_closed_domain_and_section_names(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    viewer = SimpleNamespace(
        config=config,
        state=ViewerState(config),
        sidebar_items=[{"type": "GridUnitSetting"}],
    )
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))
    sidebar = SideBarRight(SimpleNamespace())

    sidebar.set_current_tab("Annotations")
    assert sidebar.widget.tabText(sidebar.widget.currentIndex()) == "Annotations"
    sidebar.focus_system_section("Grid and Units")
    assert sidebar.widget.tabText(sidebar.widget.currentIndex()) == "System"
    assert list(sidebar.system_panel.sections) == ["Grid and Units"]

    with pytest.raises(ValueError, match="Unsupported sidebar tab"):
        cast(Any, sidebar).set_current_tab("Other")
    with pytest.raises(ValueError, match="Unsupported system section"):
        cast(Any, sidebar).focus_system_section("Other")
    with pytest.raises(ValueError, match="not configured"):
        sidebar.focus_system_section("Camera")
    assert app is not None


def test_system_sections_share_one_expanding_field_column():
    app = QApplication.instance() or QApplication([])
    camera = Container(container_type="scrollable", compact=True)
    camera.add(NumberEdit(SimpleNamespace(value=1.0), "value", title="Field of View", watch_interval=None))
    display = Container(container_type="scrollable", compact=True)
    display.add(ChoiceEdit(SimpleNamespace(value="shaded"), "value", ["shaded", "wireframe"], title="Render Mode"))
    grid = Container(container_type="scrollable", compact=True)
    grid.add(BooleanToggle(SimpleNamespace(value=True), "value", title="Show Grid"))
    panel = SystemPanel()

    panel.add_section("Camera", camera)
    panel.add_section("Display", display)
    panel.add_section("Grid and Units", grid)
    panel.widget.resize(480, 640)
    panel.widget.show()
    app.processEvents()

    rows = [camera.children[0], display.children[0], grid.children[0]]
    assert len({row.label.width() for row in rows}) == 1
    field_starts = set()
    field_right_edges = set()
    for row in rows:
        field = row.widget.layout().itemAt(1).widget()
        assert field is not None
        assert field.maximumWidth() == 16_777_215
        assert field.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding
        assert row.widget.layout().stretch(1) == 1
        field_origin = field.mapTo(panel.widget.viewport(), QPoint(0, 0))
        field_starts.add(field_origin.x())
        field_right_edges.add(field_origin.x() + field.width())
    assert len(field_starts) == 1, (field_starts, field_right_edges)
    assert len(field_right_edges) == 1, (field_starts, field_right_edges)
    assert app is not None


def test_scene_domain_uses_stable_master_detail_and_routes_optional_attributes(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    scene = ViewerScene()
    state = ViewerState(config, scene.object)
    viewer = SimpleNamespace(
        config=config,
        scene=scene,
        state=state,
        sidebar_items=[
            {
                "type": "SceneTree",
                "columns": [{"title": "Name", "type": "label", "text": lambda obj: obj.name}],
            },
            {"type": "ObjectSetting"},
            {"type": "DatastructureAttributes"},
        ],
    )
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))

    sidebar = SideBarRight(SimpleNamespace())
    layout = sidebar._page_layouts["Scene"]

    assert isinstance(sidebar.sceneform, SceneTree)
    assert isinstance(sidebar.object_setting, ObjectSetting)
    assert [sidebar.scene_details.tabText(index) for index in range(sidebar.scene_details.count())] == ["Object", "Attributes"]
    assert layout.stretch(0) == 3
    assert layout.stretch(1) == 2
    assert "DatastructureAttributes" not in [item["type"] for item in default_sidebar_items()]
    assert app is not None


def test_selection_updates_are_scoped_to_their_sidebar_domain(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    scene = ViewerScene()
    state = ViewerState(config, scene.object, scene.annotation)
    viewer = SimpleNamespace(
        config=config,
        scene=scene,
        state=state,
        sidebar_items=[
            {
                "type": "SceneTree",
                "columns": [{"title": "Name", "type": "label", "text": lambda obj: obj.name}],
            },
            {"type": "ObjectSetting"},
            {"type": "AnnotationPanel"},
        ],
    )
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))
    sidebar = SideBarRight(SimpleNamespace())
    sidebar.sceneform.update = Mock()
    sidebar.object_setting.update = Mock()
    sidebar.annotation_panel.update = Mock()

    sidebar.update_spatial_selection()

    sidebar.sceneform.update.assert_called_once_with()
    sidebar.object_setting.update.assert_called_once_with()
    sidebar.annotation_panel.update.assert_not_called()

    sidebar.update_annotation_selection()

    sidebar.annotation_panel.update.assert_called_once_with()
    sidebar.sceneform.update.assert_called_once_with()
    sidebar.object_setting.update.assert_called_once_with()
    assert app is not None
