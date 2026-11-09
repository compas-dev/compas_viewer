"""Flat Viewer controls for durable scene annotations."""

from typing import cast
from uuid import UUID

from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QColorDialog
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.colors import Color
from compas.scene import DistanceDimension
from compas.scene import SceneAnnotation

from .colorpicker import remap_rgb
from .component import Component


class AnnotationPanelItem(QTreeWidgetItem):
    """Tree item carrying one durable annotation-entry GUID."""

    annotation_guid: UUID


class AnnotationTree(QTreeWidget):
    """Annotation list that owns unmodified Delete while it has focus."""

    delete_requested = Signal()

    def event(self, event: QEvent) -> bool:
        """Reserve Delete before window-level shortcuts are activated."""
        if event.type() == QEvent.Type.ShortcutOverride and isinstance(event, QKeyEvent) and self._is_delete(event):
            event.accept()
            return True
        return super().event(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Request annotation deletion for an unmodified Delete key press."""
        if self._is_delete(event):
            self.delete_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    @staticmethod
    def _is_delete(event: QKeyEvent) -> bool:
        """Return whether an event is an unmodified Delete key press."""
        return event.key() == Qt.Key.Key_Delete and event.modifiers() == Qt.KeyboardModifier.NoModifier


class AnnotationNameEdit(QLineEdit):
    """Name editor that owns Escape while annotation details have focus."""

    escape_requested = Signal()

    def event(self, event: QEvent) -> bool:
        """Reserve Escape before window-level shortcuts are activated."""
        if event.type() == QEvent.Type.ShortcutOverride and isinstance(event, QKeyEvent) and self._is_escape(event):
            event.accept()
            return True
        return super().event(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Request local edit cancellation for unmodified Escape."""
        if self._is_escape(event):
            self.escape_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    @staticmethod
    def _is_escape(event: QKeyEvent) -> bool:
        """Return whether an event is an unmodified Escape key press."""
        return event.key() == Qt.Key.Key_Escape and event.modifiers() == Qt.KeyboardModifier.NoModifier


class AnnotationPanel(Component):
    """Display ordered annotations and details for the current selection."""

    def __init__(self) -> None:
        super().__init__()
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tree = AnnotationTree()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name", "Type", "Visible"])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.delete_requested.connect(self.remove_selected)
        self.layout.addWidget(self.tree, 3)

        self.details_group = QGroupBox("Details")
        self.details_layout = QVBoxLayout(self.details_group)
        self.details_message = QLabel("No annotation selected")
        self.details_message.setWordWrap(True)
        self.details_layout.addWidget(self.details_message)

        self.details_form_widget = QWidget()
        self.details_form = QFormLayout(self.details_form_widget)
        self.name_edit = AnnotationNameEdit()
        self.name_edit.editingFinished.connect(self._commit_name)
        self.name_edit.escape_requested.connect(self._cancel_name_edit)
        self.type_label = QLabel()
        self.details_form.addRow("Name", self.name_edit)
        self.details_form.addRow("Type", self.type_label)
        self.details_layout.addWidget(self.details_form_widget)

        self.style_group = QGroupBox("Dimension Style")
        self.style_layout = QFormLayout(self.style_group)
        self.color_button = QPushButton()
        self.color_button.clicked.connect(self._choose_color)
        self.style_layout.addRow("Color", self.color_button)
        self.line_width = self._style_spinbox(0.1)
        self.text_size = self._style_spinbox(0.1)
        self.arrow_size = self._style_spinbox(0.1)
        self.label_offset = self._style_spinbox(-10000.0)
        self.style_layout.addRow("Line Width", self.line_width)
        self.style_layout.addRow("Text Size", self.text_size)
        self.style_layout.addRow("Arrow Size", self.arrow_size)
        self.style_layout.addRow("Label Offset", self.label_offset)
        self.details_layout.addWidget(self.style_group)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        self.details_layout.addWidget(self.remove_button)
        self.layout.addWidget(self.details_group, 2)

        self.line_width.valueChanged.connect(lambda value: self._set_style("line_width", value))
        self.text_size.valueChanged.connect(lambda value: self._set_style("text_size", value))
        self.arrow_size.valueChanged.connect(lambda value: self._set_style("arrow_size", value))
        self.label_offset.valueChanged.connect(lambda value: self._set_style("label_offset", value))

        self._items: dict[UUID, AnnotationPanelItem] = {}
        self._refreshing = False
        self._sync_details()

    def update(self) -> None:
        """Synchronize the list, selection, visibility, and detail controls."""
        self._refreshing = True
        try:
            self.tree.clear()
            self._items = {}
            for annotation in self.scene.annotations:
                item = AnnotationPanelItem([annotation.name, self._item_type_name(annotation), ""])
                item.annotation_guid = annotation.guid
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(2, Qt.CheckState.Checked if annotation.show else Qt.CheckState.Unchecked)
                self.tree.addTopLevelItem(item)
                item.setSelected(annotation in self.viewer.state.annotation_selection)
                self._items[annotation.guid] = item
            self.tree.resizeColumnToContents(0)
            self.tree.resizeColumnToContents(1)
            self._sync_details()
        finally:
            self._refreshing = False

    def remove_selected(self) -> None:
        """Remove selected annotation entries without affecting spatial objects."""
        entries = tuple(self.viewer.state.annotation_selection)
        for annotation in entries:
            self.scene.remove_annotation(annotation)
        self.update()

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """Apply durable visibility edits from the flat list."""
        if self._refreshing or column != 2:
            return
        annotation = self.scene.annotation(cast(AnnotationPanelItem, item).annotation_guid)
        annotation.show = item.checkState(2) == Qt.CheckState.Checked
        self.viewer.refresh_annotations((annotation,))

    def _on_selection_changed(self) -> None:
        """Synchronize annotation selection without changing spatial selection."""
        if self._refreshing:
            return
        selected = tuple(self.scene.annotation(cast(AnnotationPanelItem, item).annotation_guid) for item in self.tree.selectedItems())
        self.viewer.state.annotation_selection.replace(selected)
        self._sync_details()

    def _sync_details(self) -> None:
        """Display details for zero, one, or multiple selected annotations."""
        selected = self.viewer.state.annotation_selection.objects
        if len(selected) == 0:
            self.details_message.setText("No annotation selected")
            self.details_message.show()
            self.details_form_widget.hide()
            self.style_group.hide()
            self.remove_button.hide()
            return
        if len(selected) > 1:
            self.details_message.setText(f"{len(selected)} annotations selected")
            self.details_message.show()
            self.details_form_widget.hide()
            self.style_group.hide()
            self.remove_button.show()
            return

        annotation = selected[0]
        self.details_message.hide()
        self.details_form_widget.show()
        self.remove_button.show()
        self.name_edit.setText(annotation.name)
        self.type_label.setText(self._item_type_name(annotation))
        self._sync_style_controls()

    def _sync_style_controls(self) -> None:
        """Display style fields for one selected distance dimension."""
        annotation = self._selected_dimension()
        if annotation is None or annotation.style is None:
            self.style_group.hide()
            return
        self.style_group.show()
        style = annotation.style
        controls = (
            (self.line_width, style.line_width),
            (self.text_size, style.text_size),
            (self.arrow_size, style.arrow_size),
            (self.label_offset, style.label_offset),
        )
        for control, value in controls:
            control.blockSignals(True)
            control.setValue(value)
            control.blockSignals(False)
        self._set_color_button(style.color)

    def _selected_annotation(self) -> SceneAnnotation | None:
        """Return the only selected annotation entry."""
        selected = self.viewer.state.annotation_selection.objects
        return selected[0] if len(selected) == 1 else None

    def _selected_dimension(self) -> SceneAnnotation | None:
        """Return the only selected distance-dimension entry."""
        annotation = self._selected_annotation()
        if annotation is None:
            return None
        try:
            return annotation if isinstance(annotation.item, DistanceDimension) else None
        except LookupError:
            return None

    def _commit_name(self) -> None:
        """Commit the explicit Name field without rebuilding render resources."""
        annotation = self._selected_annotation()
        if annotation is None:
            return
        name = self.name_edit.text()
        if name == annotation.name:
            return
        annotation.name = name
        item = self._items.get(annotation.guid)
        if item is not None:
            item.setText(0, name)

    def _cancel_name_edit(self) -> None:
        """Restore the current durable name and leave the editor."""
        annotation = self._selected_annotation()
        if annotation is not None:
            self.name_edit.setText(annotation.name)
        self.name_edit.clearFocus()

    def _set_style(self, name: str, value: float) -> None:
        """Set one durable dimension-style field and refresh its render layer."""
        if self._refreshing:
            return
        annotation = self._selected_dimension()
        if annotation is None or annotation.style is None:
            return
        setattr(annotation.style, name, value)
        self.viewer.refresh_annotations((annotation,))

    def _choose_color(self) -> None:
        """Choose a durable dimension color for the selected entry."""
        annotation = self._selected_dimension()
        if annotation is None or annotation.style is None:
            return
        current = QColor(*remap_rgb(annotation.style.color.rgb, to_range_one=False))
        color = QColorDialog.getColor(current, self.widget)
        if not color.isValid():
            return
        red, green, blue, _alpha = cast(tuple[int, int, int, int], color.getRgb())
        annotation.style.color = Color.from_rgb255(red, green, blue)
        self._set_color_button(annotation.style.color)
        self.viewer.refresh_annotations((annotation,))

    def _set_color_button(self, color: Color) -> None:
        """Display one COMPAS color on the style button."""
        qcolor = QColor(*remap_rgb(color.rgb, to_range_one=False))
        self.color_button.setText(qcolor.name())
        self.color_button.setStyleSheet(f"background-color: {qcolor.name()};")

    @staticmethod
    def _item_type_name(annotation: SceneAnnotation) -> str:
        """Return the resolved semantic item type name."""
        try:
            return type(annotation.item).__name__
        except LookupError:
            return "Unresolved"

    @staticmethod
    def _style_spinbox(minimum: float) -> QDoubleSpinBox:
        """Create one logical-pixel style editor."""
        control = QDoubleSpinBox()
        control.setDecimals(1)
        control.setSingleStep(0.5)
        control.setRange(minimum, 10000.0)
        return control


__all__ = ["AnnotationPanel"]
