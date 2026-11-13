from types import SimpleNamespace
from typing import Any
from typing import cast
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.geometry import Point
from compas.geometry import Sphere
from compas_viewer._theme import application_stylesheet
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
        "DataPanel",
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


def test_sidebar_resolves_contextual_deletion_from_focus_and_active_tab():
    app = QApplication.instance() or QApplication([])
    sidebar = object.__new__(SideBarRight)
    sidebar.widget = QTabWidget()
    sidebar.pages = {}
    for name in sidebar.TABS:
        page = QWidget()
        page.setLayout(QVBoxLayout())
        sidebar.pages[name] = page
        sidebar.widget.addTab(page, name)
    renderer = QWidget()
    renderer.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    sidebar.viewport = SimpleNamespace(renderer=renderer)

    annotation_control = QPushButton("Annotation")
    annotation_editor = QLineEdit()
    sidebar.pages["Annotations"].layout().addWidget(annotation_control)
    sidebar.pages["Annotations"].layout().addWidget(annotation_editor)
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(renderer)
    layout.addWidget(sidebar.widget)
    window.show()

    sidebar.set_current_tab("Annotations")
    annotation_control.setFocus()
    app.processEvents()
    assert sidebar.deletion_domain(use_focus=True) == "annotations"

    annotation_editor.setFocus()
    app.processEvents()
    assert sidebar.deletion_domain(use_focus=True) is None

    renderer.setFocus()
    app.processEvents()
    assert sidebar.deletion_domain(use_focus=True) == "spatial"

    sidebar.set_current_tab("Scene")
    assert sidebar.deletion_domain(use_focus=False) == "spatial"
    sidebar.set_current_tab("Annotations")
    assert sidebar.deletion_domain(use_focus=False) == "annotations"
    sidebar.set_current_tab("System")
    assert sidebar.deletion_domain(use_focus=False) is None
    window.hide()


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


def test_sidebar_has_exactly_four_stable_domains_without_splitters(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    viewer = SimpleNamespace(config=config, state=ViewerState(config), sidebar_items=[])
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))

    sidebar = SideBarRight(SimpleNamespace())

    assert [sidebar.widget.tabText(index) for index in range(sidebar.widget.count())] == ["Scene", "Data", "Annotations", "System"]
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


def test_camera_settings_are_complete_before_system_panel_sizing(monkeypatch, request):
    app = QApplication.instance() or QApplication([])
    previous_stylesheet = app.styleSheet()
    request.addfinalizer(lambda: app.setStyleSheet(previous_stylesheet))
    config = Config()
    camera = SimpleNamespace(
        target=Point(*config.camera.target),
        position=Point(*config.camera.position),
        fov=config.camera.fov,
        near=config.camera.near,
        far=config.camera.far,
        scale=config.camera.scale,
        zoomdelta=config.camera.zoomdelta,
        rotationdelta=config.camera.rotationdelta,
        pandelta=config.camera.pandelta,
    )
    renderer = SimpleNamespace(camera=camera, update=Mock())
    viewport = SimpleNamespace(renderer=renderer)
    viewer = SimpleNamespace(
        config=config,
        state=ViewerState(config),
        sidebar_items=[{"type": "CameraSetting"}],
    )
    assert not hasattr(viewer, "ui")
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))

    sidebar = SideBarRight(viewport)

    assert len(sidebar.camera_setting.children) == 14
    initial_height = sidebar.camera_setting.widget.height()
    assert initial_height > 14 * 20

    sidebar.update()
    sidebar.set_current_tab("System")
    app.setStyleSheet(application_stylesheet("dark"))
    app.processEvents()

    assert len(sidebar.camera_setting.children) == 14
    assert sidebar.camera_setting.widget.height() == initial_height


def test_system_sections_share_one_expanding_field_column(request):
    app = QApplication.instance() or QApplication([])
    previous_stylesheet = app.styleSheet()
    request.addfinalizer(lambda: app.setStyleSheet(previous_stylesheet))
    app.setStyleSheet(application_stylesheet("light"))
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

    assert panel.layout.spacing() == 14
    groups = [panel.sections[name][0] for name in ("Camera", "Display", "Grid and Units")]
    for group in groups:
        assert group.objectName() == "systemSection"
        assert group.font().bold()
        assert group.font().pointSizeF() == pytest.approx(12.0)
        margins = group.layout().contentsMargins()
        assert margins.top() == 12
        assert margins.bottom() == 12

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
    assert layout.itemAt(0).widget() is sidebar.scene_splitter
    assert sidebar.scene_splitter.count() == 2
    assert sidebar.scene_splitter.widget(0) is sidebar.sceneform.widget
    assert sidebar.scene_splitter.widget(1) is sidebar.scene_details
    assert not sidebar.scene_splitter.isCollapsible(0)
    assert not sidebar.scene_splitter.isCollapsible(1)
    assert "DatastructureAttributes" not in [item["type"] for item in default_sidebar_items()]
    assert app is not None


def test_scene_and_annotation_splitters_are_independent_and_preserve_user_sizes(monkeypatch):
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
    sidebar.widget.resize(420, 700)
    sidebar.widget.show()
    app.processEvents()
    sidebar.scene_splitter.setSizes([180, 420])
    sidebar.annotation_panel.splitter.setSizes([400, 200])
    app.processEvents()
    scene_sizes = sidebar.scene_splitter.sizes()
    annotation_sizes = sidebar.annotation_panel.splitter.sizes()

    sidebar.update_spatial_selection()
    sidebar.update_annotation_selection()
    app.processEvents()

    assert sidebar.scene_splitter.sizes() == scene_sizes
    assert sidebar.annotation_panel.splitter.sizes() == annotation_sizes
    assert sidebar.scene_splitter is not sidebar.annotation_panel.splitter
    sidebar.widget.hide()


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
