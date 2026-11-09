from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.geometry import Point
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
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
    assert panel.layout.stretch(0) == 3
    assert panel.layout.stretch(1) == 2
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

    item.setCheckState(2, Qt.CheckState.Unchecked)
    panel.line_width.setValue(6.0)

    assert viewer.state.annotation_selection.objects == (entry,)
    assert not entry.show
    assert entry.style is not None
    assert entry.style.line_width == 6.0
    assert not panel.style_group.isHidden()
    assert viewer.refresh_annotations.call_count >= 2


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


def test_annotation_panel_handles_unresolved_entries_and_removes_only_annotations(monkeypatch):
    panel, viewer, scene, _app = annotation_panel(monkeypatch)
    spatial = scene.add(Point(0, 0, 0))
    scene.add_annotation_reference(uuid4(), name="Missing")
    panel.update()
    item = panel.tree.topLevelItem(0)
    item.setSelected(True)
    panel._on_selection_changed()

    assert panel._selected_dimension() is None
    assert panel.style_group.isHidden()
    assert panel.type_label.text() == "Unresolved"

    panel.remove_selected()

    assert scene.annotations == ()
    assert scene.objects == [spatial]
    assert viewer.state.annotation_selection.objects == ()
