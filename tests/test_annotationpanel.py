from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import call
from uuid import uuid4

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QColor
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QColorDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import ArrowAnnotation
from compas.scene import ComponentAnchor
from compas.scene import DistanceDimension
from compas.scene import DistanceDimensionLayout
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer import Viewer
from compas_viewer.components.annotationpanel import AnnotationPanel
from compas_viewer.config import Config
from compas_viewer.scene import ViewerScene
from compas_viewer.state import ViewerState


def annotation_panel(monkeypatch):
    app = QApplication.instance() or QApplication([])
    scene = ViewerScene()
    state = ViewerState(Config(), scene.object, scene.annotation)
    viewer = SimpleNamespace(
        scene=scene,
        state=state,
        running=False,
        refresh_annotations=Mock(),
        renderer=Mock(),
        ui=SimpleNamespace(sidebar=Mock()),
    )
    scene.attach(viewer)
    monkeypatch.setattr(AnnotationPanel, "viewer", property(lambda _self: viewer), raising=False)
    return AnnotationPanel(), viewer, scene, app


def test_annotation_panel_is_flat_ordered_read_only_and_stably_split(monkeypatch):
    panel, _viewer, scene, app = annotation_panel(monkeypatch)
    first = scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)), name="First")
    second = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
        name="Second",
    )

    panel.update()

    assert panel.tree.topLevelItemCount() == 2
    assert panel.tree.topLevelItem(0).text(0) == first.name
    assert panel.tree.topLevelItem(0).text(1) == "TextAnnotation"
    assert panel.tree.topLevelItem(1).text(0) == second.name
    assert panel.tree.topLevelItem(1).text(1) == "DistanceDimension"
    assert panel.tree.editTriggers() == QAbstractItemView.EditTrigger.NoEditTriggers
    assert not panel.tree.topLevelItem(0).flags() & Qt.ItemFlag.ItemIsEditable
    assert panel.splitter.count() == 2
    assert panel.splitter.widget(0) is panel.tree
    assert panel.splitter.widget(1) is panel.details_scroll
    assert panel.details_scroll.widget() is panel.details_group
    assert panel.details_scroll.widgetResizable()
    assert panel.details_scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    assert not panel.splitter.isCollapsible(0)
    assert not panel.splitter.isCollapsible(1)
    assert app is not None


def test_focused_annotation_tree_owns_delete_without_conflicting_with_window_action(monkeypatch):
    panel, _viewer, scene, app = annotation_panel(monkeypatch)
    scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)))
    panel.update()
    panel.tree.topLevelItem(0).setSelected(True)
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(panel.widget)
    other = QPushButton("Other")
    layout.addWidget(other)
    window_delete = Mock()
    action = QAction("Delete Selected", window)
    action.setShortcut(QKeySequence("Delete"))
    action.triggered.connect(window_delete)
    window.addAction(action)
    window.show()
    panel.tree.setFocus()
    app.processEvents()

    QTest.keyClick(panel.tree, Qt.Key.Key_Delete)
    app.processEvents()
    assert scene.annotations == ()
    window_delete.assert_not_called()

    other.setFocus()
    app.processEvents()
    QTest.keyClick(other, Qt.Key.Key_Delete)
    app.processEvents()
    window_delete.assert_called_once_with()

    window.hide()


def test_annotation_panel_edits_explicit_name_visibility_selection_and_style(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
        name="Length",
    )
    panel.update()
    item = panel.tree.topLevelItem(0)

    item.setSelected(True)
    panel._on_selection_changed()
    viewer.refresh_annotations.reset_mock()
    panel.name_edit.setText("Span")
    panel.name_edit.editingFinished.emit()

    assert entry.name == "Span"
    assert item.text(0) == "Span"
    viewer.refresh_annotations.assert_not_called()
    assert not panel.details_form_widget.isHidden()
    assert panel.type_label.text() == "DistanceDimension"
    assert not panel.format_group.isHidden()

    item.setCheckState(2, Qt.CheckState.Unchecked)
    panel.line_width.setValue(6.0)
    panel.extension_line_width.setValue(1.5)

    assert viewer.state.annotation_selection.objects == (entry,)
    assert not entry.show
    assert entry.style is not None
    assert entry.style.line_width == 6.0
    assert entry.style.extension_line_width == 1.5
    assert not panel.style_group.isHidden()
    assert viewer.refresh_annotations.call_args_list[-2:] == [call((entry,)), call((entry,))]
    viewer.renderer.rebuild_buffers.assert_not_called()


def test_annotation_details_scroll_without_collapsing_controls_and_preserve_split(monkeypatch):
    panel, viewer, scene, app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])))
    panel.update()
    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(panel.widget)
    window.resize(420, 360)
    window.show()
    app.processEvents()

    groups = (panel.format_group, panel.style_group, panel.layout_group, panel.background_group)
    minimum_heights = [group.minimumSizeHint().height() for group in groups]
    panel.splitter.setSizes([250, 80])
    app.processEvents()
    compact_sizes = panel.splitter.sizes()
    compact_scroll_maximum = panel.details_scroll.verticalScrollBar().maximum()

    assert compact_scroll_maximum > 0
    assert all(group.height() >= minimum for group, minimum in zip(groups, minimum_heights, strict=True))
    assert panel.details_layout.indexOf(panel.format_group) < panel.details_layout.indexOf(panel.style_group)
    assert panel.details_layout.indexOf(panel.style_group) < panel.details_layout.indexOf(panel.layout_group)
    assert panel.details_layout.indexOf(panel.layout_group) < panel.details_layout.indexOf(panel.background_group)

    panel.update()
    app.processEvents()
    assert panel.splitter.sizes() == compact_sizes
    assert panel.details_scroll.verticalScrollBar().maximum() > 0

    window.resize(420, 900)
    panel.splitter.setSizes([80, 800])
    app.processEvents()
    assert panel.details_scroll.verticalScrollBar().maximum() < compact_scroll_maximum
    window.hide()


def test_annotation_panel_edits_optional_label_background(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)))
    panel.update()
    panel.tree.topLevelItem(0).setSelected(True)
    panel._on_selection_changed()
    viewer.refresh_annotations.reset_mock()

    assert not panel.background_group.isHidden()
    assert not panel.background_enabled.isChecked()
    assert not panel.background_color_button.isEnabled()
    assert not panel.background_padding.isEnabled()

    panel.background_enabled.setChecked(True)

    assert entry.label_background == Color.white()
    assert panel.background_color_button.isEnabled()
    assert panel.background_padding.isEnabled()
    assert viewer.refresh_annotations.call_args_list == [call((entry,))]

    panel.background_padding.setValue(5.5)

    assert entry.label_background_padding == 5.5
    assert viewer.refresh_annotations.call_args_list == [call((entry,)), call((entry,))]

    monkeypatch.setattr(
        QColorDialog,
        "getColor",
        Mock(return_value=QColor.fromRgb(10, 20, 30, 128)),
    )
    panel.background_color_button.click()

    assert entry.label_background is not None
    assert entry.label_background.rgba == pytest.approx((10 / 255, 20 / 255, 30 / 255, 128 / 255))
    assert panel.background_color_button.text() == "#800a141e"
    assert viewer.refresh_annotations.call_args_list == [call((entry,)), call((entry,)), call((entry,))]

    panel.background_enabled.setChecked(False)

    assert entry.label_background is None
    assert entry.label_background_padding == 5.5
    assert not panel.background_color_button.isEnabled()
    assert not panel.background_padding.isEnabled()
    assert viewer.refresh_annotations.call_args_list == [call((entry,)), call((entry,)), call((entry,)), call((entry,))]


def test_label_background_controls_require_one_resolved_text_bearing_annotation(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    text = scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)))
    dimension = scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])))
    arrow = scene.add_annotation(ArrowAnnotation(Point(0, 0, 0), Point(1, 0, 0)))
    unresolved = scene.add_annotation_reference(uuid4(), name="Missing")
    panel.update()

    for entry in (text, dimension):
        viewer.state.annotation_selection.replace((entry,))
        panel._sync_details()
        assert not panel.background_group.isHidden()

    for selection in ((arrow,), (unresolved,), (text, dimension)):
        viewer.state.annotation_selection.replace(selection)
        panel._sync_details()
        assert panel.background_group.isHidden()


def test_invalid_label_background_padding_preserves_background_atomically(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    background = Color(0.1, 0.2, 0.3, 0.4)
    entry = scene.add_annotation(
        TextAnnotation("A", Point(0, 0, 0)),
        label_background=background,
        label_background_padding=4.0,
    )
    panel.update()
    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()
    viewer.refresh_annotations.reset_mock()

    with pytest.raises(ValueError, match="padding.*negative"):
        panel._set_background_padding(-1.0)

    assert panel.background_enabled.isChecked()
    assert entry.label_background is background
    assert entry.label_background_padding == 4.0
    assert panel.background_color_button.text() == "#661a334d"
    assert panel.background_padding.value() == 4.0
    viewer.refresh_annotations.assert_not_called()


def test_visibility_checkbox_redraws_without_rebuilding_emitting_item(monkeypatch):
    app = QApplication.instance() or QApplication([])
    scene = ViewerScene()
    config = Config()
    viewer = object.__new__(Viewer)
    viewer._config = config
    viewer._scene = scene
    viewer.running = False
    viewer.state = ViewerState(config, scene.object, scene.annotation)
    renderer = Mock()
    sidebar = Mock()
    viewer.ui = SimpleNamespace(
        viewport=SimpleNamespace(renderer=renderer),
        sidebar=sidebar,
    )
    scene.attach(viewer)
    annotation = scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)))
    render_object = Mock(_inited=True)
    scene.annotation_render_objects[annotation.guid] = render_object
    viewer.running = True
    monkeypatch.setattr(AnnotationPanel, "viewer", property(lambda _self: viewer), raising=False)
    panel = AnnotationPanel()
    panel.update()
    item = panel.tree.topLevelItem(0)

    item.setCheckState(2, Qt.CheckState.Unchecked)

    assert not annotation.show
    assert panel.tree.topLevelItem(0) is item
    assert item.text(0) == annotation.name
    render_object.update.assert_called_once_with(update_data=True)
    renderer.makeCurrent.assert_called_once_with()
    renderer.doneCurrent.assert_called_once_with()
    renderer.update.assert_called_once_with()
    sidebar.update.assert_not_called()
    sidebar.update_spatial_selection.assert_not_called()
    sidebar.update_annotation_selection.assert_not_called()
    assert app is not None


def test_annotation_panel_shows_none_multiple_and_single_detail_states(monkeypatch):
    panel, _viewer, scene, _app = annotation_panel(monkeypatch)
    scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)), name="First")
    scene.add_annotation(TextAnnotation("B", Point(1, 0, 0)), name="Second")
    panel.update()

    assert panel.details_message.text() == "No annotation selected"
    assert not panel.details_message.isHidden()
    assert panel.details_form_widget.isHidden()
    assert panel.remove_button.isHidden()

    panel.tree.topLevelItem(0).setSelected(True)
    panel.tree.topLevelItem(1).setSelected(True)
    panel._on_selection_changed()

    assert panel.details_message.text() == "2 annotations selected"
    assert not panel.details_message.isHidden()
    assert panel.details_form_widget.isHidden()
    assert not panel.remove_button.isHidden()

    panel.tree.topLevelItem(1).setSelected(False)
    panel._on_selection_changed()

    assert panel.details_message.isHidden()
    assert not panel.details_form_widget.isHidden()
    assert panel.name_edit.text() == "First"
    assert panel.style_group.isHidden()
    assert panel.format_group.isHidden()


def test_annotation_name_escape_cancels_locally_without_window_deselect(monkeypatch):
    panel, viewer, scene, app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)), name="Original")
    panel.update()
    panel.tree.topLevelItem(0).setSelected(True)
    panel._on_selection_changed()

    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(panel.widget)
    deselect = Mock()
    action = QAction("Deselect All", window)
    action.setShortcut(QKeySequence("Escape"))
    action.triggered.connect(deselect)
    window.addAction(action)
    window.show()
    panel.name_edit.setFocus()
    panel.name_edit.setText("Changed")
    app.processEvents()

    QTest.keyClick(panel.name_edit, Qt.Key.Key_Escape)
    app.processEvents()

    assert panel.name_edit.text() == "Original"
    assert entry.name == "Original"
    assert viewer.state.annotation_selection.objects == (entry,)
    deselect.assert_not_called()
    window.hide()


def test_dimension_format_edits_refresh_only_the_selected_annotation(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    spatial = scene.add(Point(5, 0, 0))
    dimension = DistanceDimension(
        PointAnchor([0, 0, 0]),
        PointAnchor([2, 0, 0]),
        unit="m",
        precision=2,
        label="Span",
    )
    entry = scene.add_annotation(dimension, name="Length", show=False)
    panel.update()
    panel.tree.topLevelItem(0).setSelected(True)
    panel._on_selection_changed()
    viewer.refresh_annotations.reset_mock()

    before = {
        "dimension": dimension,
        "entry": entry,
        "guid": entry.guid,
        "anchors": (dimension.start, dimension.end),
        "label": dimension.label,
        "style": entry.style,
        "show": entry.show,
        "annotations": tuple(scene.annotations),
        "objects": tuple(scene.objects),
        "spatial_selection": viewer.state.selection.objects,
        "annotation_selection": viewer.state.annotation_selection.objects,
        "defaults": (viewer.state.config.measurement.unit, viewer.state.config.measurement.precision),
    }

    panel.unit_edit.setText(" cm ")
    panel.unit_edit.editingFinished.emit()
    panel.precision_edit.setText("15")
    panel.precision_edit.editingFinished.emit()
    panel.precision_edit.setText("0")
    panel.precision_edit.editingFinished.emit()

    assert dimension.unit == "cm"
    assert dimension.precision == 0
    assert dimension.formatted_label(scene) == "Span"
    assert viewer.refresh_annotations.call_args_list == [call((entry,)), call((entry,)), call((entry,))]
    assert dimension is before["dimension"]
    assert entry is before["entry"]
    assert entry.guid == before["guid"]
    assert (dimension.start, dimension.end) == before["anchors"]
    assert dimension.label == before["label"]
    assert entry.style is before["style"]
    assert entry.show is before["show"]
    assert tuple(scene.annotations) == before["annotations"]
    assert tuple(scene.objects) == before["objects"] == (spatial,)
    assert viewer.state.selection.objects == before["spatial_selection"]
    assert viewer.state.annotation_selection.objects == before["annotation_selection"]
    assert (viewer.state.config.measurement.unit, viewer.state.config.measurement.precision) == before["defaults"]
    viewer.renderer.rebuild_buffers.assert_not_called()

    viewer.refresh_annotations.reset_mock()
    panel.unit_edit.setText(" cm ")
    panel.unit_edit.editingFinished.emit()
    panel.precision_edit.setText("0")
    panel.precision_edit.editingFinished.emit()
    viewer.refresh_annotations.assert_not_called()


def test_dimension_unit_escape_restores_durable_value_without_deselect(monkeypatch):
    panel, viewer, scene, app = annotation_panel(monkeypatch)
    dimension = DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0]), unit="mm")
    entry = scene.add_annotation(dimension)
    panel.update()
    panel.tree.topLevelItem(0).setSelected(True)
    panel._on_selection_changed()
    viewer.refresh_annotations.reset_mock()

    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(panel.widget)
    deselect = Mock()
    action = QAction("Deselect All", window)
    action.setShortcut(QKeySequence("Escape"))
    action.triggered.connect(deselect)
    window.addAction(action)
    window.show()
    panel.unit_edit.setFocus()
    panel.unit_edit.setText("cm")
    app.processEvents()

    QTest.keyClick(panel.unit_edit, Qt.Key.Key_Escape)
    app.processEvents()

    assert panel.unit_edit.text() == "mm"
    assert not panel.unit_edit.hasFocus()
    assert dimension.unit == "mm"
    assert viewer.state.annotation_selection.objects == (entry,)
    viewer.refresh_annotations.assert_not_called()
    deselect.assert_not_called()

    panel.precision_edit.setFocus()
    panel.precision_edit.setText("15")
    app.processEvents()
    QTest.keyClick(panel.precision_edit, Qt.Key.Key_Escape)
    app.processEvents()

    assert panel.precision_edit.text() == "2"
    assert not panel.precision_edit.hasFocus()
    assert dimension.precision == 2
    assert viewer.state.annotation_selection.objects == (entry,)
    viewer.refresh_annotations.assert_not_called()
    deselect.assert_not_called()

    panel.unit_edit.setText("   ")
    panel.unit_edit.editingFinished.emit()
    assert dimension.unit is None
    viewer.refresh_annotations.assert_called_once_with((entry,))
    window.hide()


def test_measurement_format_group_requires_one_resolved_dimension_item(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    text = scene.add_annotation(TextAnnotation("A", Point(0, 0, 0)))
    arrow = scene.add_annotation(ArrowAnnotation(Point(0, 0, 0), Point(1, 0, 0)))
    unresolved_entry = scene.add_annotation_reference(uuid4(), name="Missing")
    unresolved_anchors = DistanceDimension(
        ComponentAnchor(uuid4(), "point"),
        ComponentAnchor(uuid4(), "point"),
        unit="m",
        precision=3,
    )
    dimension_entry = scene.add_annotation(unresolved_anchors)
    panel.update()

    assert panel.format_group.isHidden()
    for entry in (text, arrow, unresolved_entry):
        viewer.state.annotation_selection.replace((entry,))
        panel._sync_details()
        assert panel.format_group.isHidden()

    viewer.state.annotation_selection.replace((text, dimension_entry))
    panel._sync_details()
    assert panel.format_group.isHidden()

    viewer.state.annotation_selection.replace((dimension_entry,))
    panel._sync_details()
    assert not panel.format_group.isHidden()
    assert panel.unit_edit.text() == "m"
    assert panel.precision_edit.text() == "3"
    assert unresolved_anchors.resolve(scene) is None


def test_measurement_format_synchronization_blocks_editor_signals(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0]), unit="cm", precision=5))
    unit_changed = Mock()
    precision_changed = Mock()
    panel.unit_edit.textChanged.connect(unit_changed)
    panel.precision_edit.textChanged.connect(precision_changed)

    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()

    assert panel.unit_edit.text() == "cm"
    assert panel.precision_edit.text() == "5"
    unit_changed.assert_not_called()
    precision_changed.assert_not_called()


def test_spatial_layout_edits_replace_atomically_and_refresh_only_annotation(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([4, 0, 0])))
    panel.update()
    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()
    viewer.refresh_annotations.reset_mock()

    assert not panel.layout_group.isHidden()
    assert panel.layout_status.text() == "Resolved — no displacement"
    panel.layout_offset.setText("-2.5")
    panel.layout_normal_x.setText("0")
    panel.layout_normal_y.setText("0")
    panel.layout_normal_z.setText("3")
    panel.layout_apply.click()

    assert entry.layout == DistanceDimensionLayout(-2.5, Vector(0, 0, 3))
    assert panel.layout_status.text() == "Resolved"
    viewer.refresh_annotations.assert_called_once_with((entry,))
    viewer.renderer.rebuild_buffers.assert_not_called()


@pytest.mark.parametrize(
    ("offset", "normal"),
    [
        ("nan", ("0", "0", "1")),
        ("1", ("0", "", "1")),
        ("1", ("0", "inf", "1")),
    ],
)
def test_invalid_spatial_layout_restores_complete_durable_value_without_refresh(monkeypatch, offset, normal):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    original = DistanceDimensionLayout(2.0, Vector(0, 1, 0))
    entry = scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])), layout=original)
    panel.update()
    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()
    viewer.refresh_annotations.reset_mock()

    panel.layout_offset.setText(offset)
    for control, value in zip((panel.layout_normal_x, panel.layout_normal_y, panel.layout_normal_z), normal, strict=True):
        control.setText(value)
    panel.layout_apply.click()

    assert entry.layout is original
    assert panel.layout_offset.text() == "2.0"
    assert [panel.layout_normal_x.text(), panel.layout_normal_y.text(), panel.layout_normal_z.text()] == ["0.0", "1.0", "0.0"]
    viewer.refresh_annotations.assert_not_called()


def test_spatial_layout_escape_and_reset_preserve_selection_and_refresh_contract(monkeypatch):
    panel, viewer, scene, app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
        layout=DistanceDimensionLayout(2.0, Vector(0, 0, 1)),
    )
    panel.update()
    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()
    viewer.refresh_annotations.reset_mock()
    panel.layout_offset.setFocus()
    panel.layout_offset.setText("9")

    QTest.keyClick(panel.layout_offset, Qt.Key.Key_Escape)
    app.processEvents()

    assert entry.layout == DistanceDimensionLayout(2.0, Vector(0, 0, 1))
    assert panel.layout_offset.text() == "2.0"
    assert viewer.state.annotation_selection.objects == (entry,)
    viewer.refresh_annotations.assert_not_called()

    panel.layout_reset.click()

    assert entry.layout == DistanceDimensionLayout()
    assert panel.layout_status.text() == "Resolved — no displacement"
    viewer.refresh_annotations.assert_called_once_with((entry,))


def test_spatial_layout_keyboard_traversal_retains_draft_until_one_apply(monkeypatch):
    panel, viewer, scene, app = annotation_panel(monkeypatch)
    entry = scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([2, 0, 0])))
    panel.update()
    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()
    viewer.refresh_annotations.reset_mock()
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(panel.widget)
    window.show()

    panel.layout_offset.setFocus()
    QTest.keyClick(panel.layout_offset, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
    QTest.keyClicks(panel.layout_offset, "2.5")
    QTest.keyClick(panel.layout_offset, Qt.Key.Key_Tab)
    QTest.keyClicks(panel.layout_normal_x, "0")
    QTest.keyClick(panel.layout_normal_x, Qt.Key.Key_Tab)
    QTest.keyClicks(panel.layout_normal_y, "0")
    QTest.keyClick(panel.layout_normal_y, Qt.Key.Key_Tab)
    QTest.keyClicks(panel.layout_normal_z, "1")
    app.processEvents()

    assert [panel.layout_offset.text(), panel.layout_normal_x.text(), panel.layout_normal_y.text(), panel.layout_normal_z.text()] == ["2.5", "0", "0", "1"]
    assert entry.layout == DistanceDimensionLayout()
    viewer.refresh_annotations.assert_not_called()

    panel.layout_apply.click()

    assert entry.layout == DistanceDimensionLayout(2.5, Vector(0, 0, 1))
    viewer.refresh_annotations.assert_called_once_with((entry,))
    window.close()


@pytest.mark.parametrize("invalid", ["", "   ", "-1", "16", "2147483648", "1.5", "not-an-integer"])
def test_invalid_dimension_precision_restores_atomically(monkeypatch, invalid):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    dimension = DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0]), precision=7)
    entry = scene.add_annotation(dimension)
    panel.update()
    viewer.state.annotation_selection.replace((entry,))
    panel._sync_details()
    viewer.refresh_annotations.reset_mock()

    panel.precision_edit.setText(invalid)
    panel.precision_edit.editingFinished.emit()

    assert dimension.precision == 7
    assert panel.precision_edit.text() == "7"
    viewer.refresh_annotations.assert_not_called()


def test_annotation_panel_handles_unresolved_entries_and_removes_only_annotations(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    spatial = scene.add(Point(0, 0, 0))
    scene.add_annotation_reference(uuid4(), name="Missing")
    panel.update()
    item = panel.tree.topLevelItem(0)
    item.setSelected(True)
    panel._on_selection_changed()

    assert panel._selected_dimension() is None
    assert panel.format_group.isHidden()
    assert panel.style_group.isHidden()
    assert panel.type_label.text() == "Unresolved"

    panel.remove_selected()

    assert scene.annotations == ()
    assert scene.objects == [spatial]
    assert viewer.state.annotation_selection.objects == ()
