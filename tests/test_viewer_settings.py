from collections.abc import Iterable
from collections.abc import Iterator
from inspect import Parameter
from inspect import signature
from types import SimpleNamespace
from typing import Any
from typing import cast
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QEvent
from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from compas.colors import Color
from compas.geometry import Point
from compas_viewer._theme import application_stylesheet
from compas_viewer.base import Base
from compas_viewer.components import BooleanToggle
from compas_viewer.components import BoundComponent
from compas_viewer.components import ChoiceEdit
from compas_viewer.components import Container
from compas_viewer.components import NumberEdit
from compas_viewer.components.annotationpanel import AnnotationTree
from compas_viewer.components.menubar import _GlobalEscapeFilter
from compas_viewer.components.viewersettings import ViewerSettings
from compas_viewer.config import Config
from compas_viewer.singleton import SingletonMeta
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import UIItem
from compas_viewer.uidefinitions import default_menu_items
from compas_viewer.uidefinitions import default_settings_items
from compas_viewer.uidefinitions import default_sidebar_items
from compas_viewer.viewer import Viewer


@pytest.fixture
def isolated_viewer_singleton() -> Iterator[None]:
    """Temporarily isolate the process-local Viewer singleton."""
    missing = object()
    previous = SingletonMeta._instances.pop(Viewer, missing)
    try:
        yield
    finally:
        current = SingletonMeta._instances.pop(Viewer, None)
        if isinstance(current, Viewer) and hasattr(current, "ui"):
            window = current.ui.window.widget
            window.close()
            if isValid(window):
                window.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            current.app.processEvents()
        if previous is not missing:
            SingletonMeta._instances[Viewer] = previous


def _settings(monkeypatch, request, items=None):
    app = QApplication.instance() or QApplication([])
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
    renderer = SimpleNamespace(
        camera=camera,
        rendermode=config.renderer.rendermode,
        view=config.renderer.view,
        backgroundcolor=Color.from_hex("#FAFAFA"),
        update=Mock(),
    )
    viewer = SimpleNamespace(
        config=config,
        state=ViewerState(config),
        settings_items=default_settings_items() if items is None else items,
    )
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))
    owner = QWidget()
    settings = ViewerSettings(SimpleNamespace(widget=owner), SimpleNamespace(renderer=renderer))

    def cleanup() -> None:
        if not isValid(owner):
            return
        owner.close()
        owner.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()

    request.addfinalizer(cleanup)
    return app, viewer, owner, settings


def _constructed_viewer(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
    *,
    sidebar_items: Iterable[UIItem] | None = None,
    settings_items: Iterable[UIItem] | None = None,
) -> Viewer:
    """Construct an isolated Viewer whose components resolve this instance."""
    viewer = object.__new__(Viewer)
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))

    def cleanup() -> None:
        ui = getattr(viewer, "ui", None)
        if ui is None:
            return
        ui.window.widget.close()
        ui.window.widget.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        viewer.app.processEvents()

    request.addfinalizer(cleanup)
    Viewer.__init__(viewer, sidebar_items=sidebar_items, settings_items=settings_items)
    return viewer


def test_default_content_and_settings_compositions_are_disjoint():
    assert [item["type"] for item in default_sidebar_items()] == [
        "SceneTree",
        "DataPanel",
        "AnnotationPanel",
        "ObjectSetting",
    ]
    assert [item["type"] for item in default_settings_items()] == [
        "CameraSetting",
        "DisplaySetting",
        "GridUnitSetting",
    ]
    view = next(item for item in default_menu_items() if item.get("title") == "View")
    assert any(item.get("title") == "Viewer Settings…" and item.get("command") == "viewer.show_viewer_settings" for item in view["items"])


def test_viewer_constructor_uses_default_compositions(monkeypatch, request):
    viewer = _constructed_viewer(monkeypatch, request)

    assert [item["type"] for item in viewer.sidebar_items] == [item["type"] for item in default_sidebar_items()]
    assert [item["type"] for item in viewer.settings_items] == [item["type"] for item in default_settings_items()]
    assert [viewer.ui.sidebar.widget.tabText(index) for index in range(viewer.ui.sidebar.widget.count())] == ["Scene", "Data", "Annotations"]
    assert list(viewer.ui.settings.sections) == ["Camera", "Display", "Grid and Units"]


def test_viewer_constructor_consumes_and_shallow_copies_setup_compositions(monkeypatch, request):
    sidebar_definition: UIItem = {"type": "DataPanel"}
    settings_definition: UIItem = {"type": "GridUnitSetting"}
    sidebar_items = [sidebar_definition]
    settings_items = (item for item in [settings_definition])

    viewer = _constructed_viewer(
        monkeypatch,
        request,
        sidebar_items=sidebar_items,
        settings_items=settings_items,
    )

    assert viewer.sidebar_items is not sidebar_items
    assert viewer.sidebar_items == [sidebar_definition]
    assert viewer.sidebar_items[0] is sidebar_definition
    assert viewer.settings_items == [settings_definition]
    assert viewer.settings_items[0] is settings_definition
    assert hasattr(viewer.ui.sidebar, "data_panel")
    assert not hasattr(viewer.ui.sidebar, "sceneform")
    assert not hasattr(viewer.ui.sidebar, "annotation_panel")
    assert list(viewer.ui.settings.sections) == ["Grid and Units"]

    sidebar_items.append({"type": "ObjectSetting"})
    viewer.sidebar_items.append({"type": "ObjectSetting"})
    viewer.settings_items.append({"type": "CameraSetting"})

    assert not hasattr(viewer.ui.sidebar, "object_setting")
    assert list(viewer.ui.settings.sections) == ["Grid and Units"]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"sidebar_items": [{"type": "Unsupported"}]}, "Unsupported sidebar item type"),
        ({"settings_items": [{"type": "Unsupported"}]}, "Unsupported settings item type"),
        ({"settings_items": [{"type": "GridUnitSetting"}, {"type": "GridUnitSetting"}]}, "Duplicate settings item type"),
        ({"sidebar_items": [{"type": "SceneTree"}]}, "Please setup config for Sceneform"),
    ],
)
def test_viewer_constructor_failure_is_atomic_and_retryable(isolated_viewer_singleton: None, kwargs, message):
    app = QApplication.instance() or QApplication([])
    windows_before = set(app.topLevelWidgets())

    with pytest.raises(ValueError, match=message):
        Viewer(**kwargs)

    assert Viewer not in SingletonMeta._instances
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    assert set(app.topLevelWidgets()) == windows_before

    tree = AnnotationTree()
    delete_requested = Mock()
    tree.delete_requested.connect(delete_requested)
    try:
        tree.show()
        tree.setFocus()
        app.processEvents()

        QTest.keyClick(tree, Qt.Key.Key_Delete)
        app.processEvents()

        delete_requested.assert_called_once_with()
    finally:
        tree.close()
        tree.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()

    viewer = Viewer(sidebar_items=[{"type": "AnnotationPanel"}], settings_items=[])
    assert SingletonMeta._instances[Viewer] is viewer
    assert hasattr(viewer.ui.sidebar, "annotation_panel")


def test_viewer_composition_inputs_are_keyword_only():
    parameters = signature(Viewer.__init__).parameters

    assert parameters["sidebar_items"].kind is Parameter.KEYWORD_ONLY
    assert parameters["settings_items"].kind is Parameter.KEYWORD_ONLY


def test_cached_viewer_preserves_first_setup_composition(isolated_viewer_singleton: None):
    first_sidebar: list[UIItem] = [{"type": "DataPanel"}]
    first_settings: list[UIItem] = [{"type": "GridUnitSetting"}]
    second_sidebar: list[UIItem] = [{"type": "AnnotationPanel"}]
    second_settings: list[UIItem] = [{"type": "DisplaySetting"}]

    first = Viewer(sidebar_items=first_sidebar, settings_items=first_settings)
    second = Viewer(sidebar_items=second_sidebar, settings_items=second_settings)

    assert second is first
    assert first.sidebar_items == first_sidebar
    assert first.settings_items == first_settings
    assert first.sidebar_items is not first_sidebar
    assert first.settings_items is not first_settings
    assert hasattr(first.ui.sidebar, "data_panel")
    assert not hasattr(first.ui.sidebar, "annotation_panel")
    assert list(first.ui.settings.sections) == ["Grid and Units"]


def test_viewer_settings_is_one_owned_initially_hidden_modeless_window(monkeypatch, request):
    app, _viewer, owner, settings = _settings(monkeypatch, request)

    assert settings.widget.parent() is owner
    assert not settings.widget.isVisible()
    assert not settings.widget.isModal()
    assert settings.widget.windowModality() == Qt.WindowModality.NonModal
    assert settings.widget.windowTitle() == "Viewer Settings"
    assert settings.widget.accessibleName() == "Viewer Settings"
    assert settings.widget.minimumWidth() >= 420
    assert settings.widget.minimumHeight() >= 480
    assert list(settings.sections) == ["Camera", "Display", "Grid and Units"]
    assert len(settings.camera_setting.children) == 14
    assert app is not None


def test_open_refreshes_and_reuses_the_same_settings_window(monkeypatch, request):
    app, _viewer, _owner, settings = _settings(monkeypatch, request)
    components = [component for _group, component in settings.sections.values()]
    for component in components:
        component.update = Mock()
    focus = Mock(wraps=settings.focus_section)
    settings.focus_section = focus
    widget = settings.widget

    settings.show("Display")
    settings.show()
    app.processEvents()

    assert settings.widget is widget
    assert settings.widget.isVisible()
    focus.assert_called_once_with("Display")
    for component in components:
        assert component.update.call_count == 2


def test_settings_navigation_accepts_only_closed_configured_sections(monkeypatch, request):
    _app, _viewer, _owner, settings = _settings(monkeypatch, request, [{"type": "GridUnitSetting"}])

    settings.show("Grid and Units")
    with pytest.raises(ValueError, match="Unsupported Viewer Settings section"):
        cast(Any, settings).show("Other")
    with pytest.raises(ValueError, match="not configured"):
        settings.show("Camera")


def test_close_hides_without_destroying_and_owner_close_releases_window(monkeypatch, request):
    app, _viewer, owner, settings = _settings(monkeypatch, request)
    widget = settings.widget
    watchers = [child for _group, component in settings.sections.values() for child in component.children if isinstance(child, BoundComponent)]
    timers = [watcher._watch_timer for watcher in watchers]
    destroyed = Mock()
    widget.destroyed.connect(destroyed)

    assert watchers
    assert all(timer is not None and timer.timer.isActive() for timer in timers)

    settings.show()
    widget.close()
    app.processEvents()

    assert not widget.isVisible()
    destroyed.assert_not_called()
    assert isValid(widget)

    settings.show()
    assert settings.widget is widget
    owner.close()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()

    destroyed.assert_called_once()
    assert not isValid(widget)
    assert all(watcher._watch_timer is None for watcher in watchers)
    assert all(timer is not None and not timer.timer.isActive() for timer in timers)
    QTest.qWait(150)


def test_window_escape_hides_settings_before_global_commands(monkeypatch, request):
    app, _viewer, _owner, settings = _settings(monkeypatch, request)
    global_callback = Mock()
    global_filter = _GlobalEscapeFilter(global_callback)
    app.installEventFilter(global_filter)
    settings.show("Camera")
    app.processEvents()

    QTest.keyClick(settings.widget, Qt.Key.Key_Escape)
    app.processEvents()

    assert not settings.widget.isVisible()
    global_callback.assert_not_called()
    app.removeEventFilter(global_filter)


def test_main_window_escape_keeps_visible_settings_and_runs_global_command(monkeypatch, request):
    app, _viewer, owner, settings = _settings(monkeypatch, request)
    global_callback = Mock()
    global_filter = _GlobalEscapeFilter(global_callback)
    app.installEventFilter(global_filter)
    owner.show()
    settings.show("Camera")
    owner.activateWindow()
    owner.setFocus()
    app.processEvents()

    assert QApplication.activeWindow() is owner
    QTest.keyClick(owner, Qt.Key.Key_Escape)
    app.processEvents()

    assert settings.widget.isVisible()
    global_callback.assert_called_once_with()
    app.removeEventFilter(global_filter)
    settings.widget.hide()


def test_combobox_popup_escape_closes_only_the_popup(monkeypatch, request):
    app, _viewer, _owner, settings = _settings(monkeypatch, request)
    global_callback = Mock()
    global_filter = _GlobalEscapeFilter(global_callback)
    app.installEventFilter(global_filter)
    settings.show("Display")
    combobox = settings.display_setting._state_controls["renderer.rendermode"].combobox
    combobox.setFocus()
    combobox.showPopup()
    app.processEvents()
    popup = QApplication.activePopupWidget()
    popup_view = combobox.view()

    assert popup is not None
    assert QApplication.focusWidget() is popup_view
    QTest.keyClick(popup_view, Qt.Key.Key_Escape)
    app.processEvents()

    assert not popup.isVisible()
    assert settings.widget.isVisible()
    global_callback.assert_not_called()
    app.removeEventFilter(global_filter)
    settings.widget.hide()


def test_editor_escape_stays_local_to_settings_editor(monkeypatch, request):
    app, _viewer, _owner, settings = _settings(monkeypatch, request)
    global_callback = Mock()
    global_filter = _GlobalEscapeFilter(global_callback)
    app.installEventFilter(global_filter)
    settings.show("Grid and Units")
    editor = settings.grid_unit_setting.precision_edit
    editor.setFocus()
    app.processEvents()

    QTest.keyClick(editor, Qt.Key.Key_Escape)
    app.processEvents()

    assert settings.widget.isVisible()
    assert editor.hasFocus()
    global_callback.assert_not_called()
    app.removeEventFilter(global_filter)
    settings.widget.hide()


def test_settings_delete_leaves_scene_selection_and_editors_independent(isolated_viewer_singleton: None):
    viewer = Viewer(settings_items=[])
    sceneobject = viewer.scene.add(Point(0, 0, 0))
    viewer.state.selection.add(sceneobject)
    settings = viewer.ui.settings
    settings.show()
    editor = QLineEdit("ab", settings.widget)
    editor.show()

    QTest.keyClick(settings.widget, Qt.Key.Key_Delete)
    assert viewer.scene.object(sceneobject.guid) is sceneobject
    assert sceneobject in viewer.state.selection

    editor.setFocus()
    editor.setCursorPosition(1)
    QTest.keyClick(editor, Qt.Key.Key_Delete)
    assert editor.text() == "a"
    assert viewer.scene.object(sceneobject.guid) is sceneobject
    assert sceneobject in viewer.state.selection


def test_settings_sections_share_one_expanding_field_column(monkeypatch, request):
    app, _viewer, _owner, settings = _settings(monkeypatch, request, [])
    previous_stylesheet = app.styleSheet()
    request.addfinalizer(lambda: app.setStyleSheet(previous_stylesheet))
    app.setStyleSheet(application_stylesheet("light"))
    camera = Container(container_type="scrollable", compact=True)
    camera.add(NumberEdit(SimpleNamespace(value=1.0), "value", title="Field of View", watch_interval=None))
    display = Container(container_type="scrollable", compact=True)
    display.add(ChoiceEdit(SimpleNamespace(value="shaded"), "value", ["shaded", "wireframe"], title="Render Mode"))
    grid = Container(container_type="scrollable", compact=True)
    grid.add(BooleanToggle(SimpleNamespace(value=True), "value", title="Show Grid"))

    settings.add_section("Camera", camera)
    settings.add_section("Display", display)
    settings.add_section("Grid and Units", grid)
    settings.widget.resize(480, 640)
    settings.widget.show()
    app.processEvents()

    assert settings.layout.spacing() == 14
    groups = [settings.sections[name][0] for name in ("Camera", "Display", "Grid and Units")]
    for group in groups:
        assert group.objectName() == "viewerSettingsSection"
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
        field_origin = field.mapTo(settings.scroll.viewport(), QPoint(0, 0))
        field_starts.add(field_origin.x())
        field_right_edges.add(field_origin.x() + field.width())
    assert len(field_starts) == 1, (field_starts, field_right_edges)
    assert len(field_right_edges) == 1, (field_starts, field_right_edges)
    settings.widget.hide()
