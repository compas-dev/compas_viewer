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


class AnnotationPanel(Component):
    """Display and edit the scene's ordered non-spatial annotations."""

    def __init__(self) -> None:
        super().__init__()
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel("Annotations")
        self.layout.addWidget(self.title)
        self.tree = AnnotationTree()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name", "Type", "Visible"])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.itemDoubleClicked.connect(self._edit_name)
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.layout.addWidget(self.tree)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        self.layout.addWidget(self.remove_button)
        self.tree.delete_requested.connect(self.remove_selected)

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
        self.layout.addWidget(self.style_group)

        self.line_width.valueChanged.connect(lambda value: self._set_style("line_width", value))
        self.text_size.valueChanged.connect(lambda value: self._set_style("text_size", value))
        self.arrow_size.valueChanged.connect(lambda value: self._set_style("arrow_size", value))
        self.label_offset.valueChanged.connect(lambda value: self._set_style("label_offset", value))

        self._items: dict[UUID, AnnotationPanelItem] = {}
        self._refreshing = False
        self.style_group.hide()

    def update(self) -> None:
        """Synchronize the flat list, selection, visibility, and style controls."""
        self._refreshing = True
        try:
            self.tree.clear()
            self._items = {}
            for annotation in self.scene.annotations:
                item = AnnotationPanelItem(
                    [
                        annotation.name,
                        self._item_type_name(annotation),
                        "",
                    ]
                )
                item.annotation_guid = annotation.guid
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(2, Qt.CheckState.Checked if annotation.show else Qt.CheckState.Unchecked)
                self.tree.addTopLevelItem(item)
                item.setSelected(annotation in self.viewer.state.annotation_selection)
                self._items[annotation.guid] = item
            self.tree.resizeColumnToContents(0)
            self.tree.resizeColumnToContents(1)
            self._sync_style_controls()
        finally:
            self._refreshing = False

    def remove_selected(self) -> None:
        """Remove selected annotation entries without affecting spatial objects."""
        entries = tuple(self.viewer.state.annotation_selection)
        for annotation in entries:
            self.scene.remove_annotation(annotation)
        self.update()

    def _edit_name(self, item: QTreeWidgetItem, column: int) -> None:
        """Start explicit inline editing only for the Name column."""
        if column == 0:
            self.tree.editItem(item, column)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """Apply durable name and visibility edits from the flat list."""
        if self._refreshing:
            return
        annotation = self.scene.annotation(cast(AnnotationPanelItem, item).annotation_guid)
        if column == 0:
            annotation.name = item.text(0)
        elif column == 2:
            annotation.show = item.checkState(2) == Qt.CheckState.Checked
        else:
            return
        self.viewer.refresh_annotations((annotation,))

    def _on_selection_changed(self) -> None:
        """Synchronize annotation selection without changing spatial selection."""
        if self._refreshing:
            return
        selected = tuple(self.scene.annotation(cast(AnnotationPanelItem, item).annotation_guid) for item in self.tree.selectedItems())
        self.viewer.state.annotation_selection.replace(selected)
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

    def _selected_dimension(self) -> SceneAnnotation | None:
        """Return the only selected distance-dimension entry."""
        selected = self.viewer.state.annotation_selection.objects
        if len(selected) != 1:
            return None
        annotation = selected[0]
        try:
            return annotation if isinstance(annotation.item, DistanceDimension) else None
        except LookupError:
            return None

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
        red, green, blue, _alpha = color.getRgb()
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
