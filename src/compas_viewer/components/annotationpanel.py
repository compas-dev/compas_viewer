"""Flat Viewer controls for durable scene annotations."""

from math import isfinite
from typing import cast
from uuid import UUID

from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QColorDialog
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.colors import Color
from compas.geometry import Vector
from compas.scene import DistanceDimension
from compas.scene import DistanceDimensionLayout
from compas.scene import SceneAnnotation
from compas.scene import TextAnnotation
from compas_viewer.dimensionlayout import resolve_dimension_layout

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


class AnnotationTextEdit(QLineEdit):
    """Annotation text editor that owns Escape while details have focus."""

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


class AnnotationIntegerEdit(AnnotationTextEdit):
    """Validated integer editor for annotation details."""


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

        self.details_group = QGroupBox("Details")
        self.details_layout = QVBoxLayout(self.details_group)
        self.details_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.details_message = QLabel("No annotation selected")
        self.details_message.setWordWrap(True)
        self.details_layout.addWidget(self.details_message)

        self.details_form_widget = QWidget()
        self.details_form = QFormLayout(self.details_form_widget)
        self.name_edit = AnnotationTextEdit()
        self.name_edit.editingFinished.connect(self._commit_name)
        self.name_edit.escape_requested.connect(self._cancel_name_edit)
        self.type_label = QLabel()
        self.details_form.addRow("Name", self.name_edit)
        self.details_form.addRow("Type", self.type_label)
        self.details_layout.addWidget(self.details_form_widget)

        self.format_group = QGroupBox("Measurement Format")
        self.format_layout = QFormLayout(self.format_group)
        self.unit_edit = AnnotationTextEdit()
        self.unit_edit.editingFinished.connect(self._commit_unit)
        self.unit_edit.escape_requested.connect(self._cancel_unit_edit)
        self.precision_edit = AnnotationIntegerEdit()
        self.precision_edit.editingFinished.connect(self._commit_precision)
        self.precision_edit.escape_requested.connect(self._cancel_precision_edit)
        self.format_layout.addRow("Coordinate Unit", self.unit_edit)
        self.format_layout.addRow("Display Precision", self.precision_edit)
        self.details_layout.addWidget(self.format_group)

        self.style_group = QGroupBox("Dimension Style")
        self.style_layout = QFormLayout(self.style_group)
        self.color_button = QPushButton()
        self.color_button.clicked.connect(self._choose_color)
        self.style_layout.addRow("Color", self.color_button)
        self.line_width = self._style_spinbox(0.1)
        self.extension_line_width = self._style_spinbox(0.1)
        self.text_size = self._style_spinbox(0.1)
        self.arrow_size = self._style_spinbox(0.1)
        self.label_offset = self._style_spinbox(-10000.0)
        self.style_layout.addRow("Dimension Line Width", self.line_width)
        self.style_layout.addRow("Extension Line Width", self.extension_line_width)
        self.style_layout.addRow("Text Size", self.text_size)
        self.style_layout.addRow("Arrow Size", self.arrow_size)
        self.style_layout.addRow("Label Offset", self.label_offset)
        self.details_layout.addWidget(self.style_group)

        self.layout_group = QGroupBox("Spatial Layout")
        self.layout_form = QFormLayout(self.layout_group)
        self.layout_offset = AnnotationTextEdit()
        self.layout_normal_x = AnnotationTextEdit()
        self.layout_normal_y = AnnotationTextEdit()
        self.layout_normal_z = AnnotationTextEdit()
        self.layout_status = QLabel()
        self.layout_status.setWordWrap(True)
        self.layout_apply = QPushButton("Apply Layout")
        self.layout_reset = QPushButton("Reset Layout")
        for control in (self.layout_offset, self.layout_normal_x, self.layout_normal_y, self.layout_normal_z):
            control.escape_requested.connect(self._cancel_layout_edit)
        self.layout_apply.clicked.connect(self._commit_layout)
        self.layout_reset.clicked.connect(self._reset_layout)
        self.layout_form.addRow("Offset", self.layout_offset)
        self.layout_form.addRow("Plane Normal X", self.layout_normal_x)
        self.layout_form.addRow("Plane Normal Y", self.layout_normal_y)
        self.layout_form.addRow("Plane Normal Z", self.layout_normal_z)
        self.layout_form.addRow("Status", self.layout_status)
        self.layout_form.addRow(self.layout_apply)
        self.layout_form.addRow(self.layout_reset)
        self.details_layout.addWidget(self.layout_group)

        self.background_group = QGroupBox("Label Background")
        self.background_layout = QFormLayout(self.background_group)
        self.background_enabled = QCheckBox()
        self.background_enabled.toggled.connect(self._set_background_enabled)
        self.background_color_button = QPushButton()
        self.background_color_button.clicked.connect(self._choose_background_color)
        self.background_padding = self._style_spinbox(0.0)
        self.background_padding.valueChanged.connect(self._set_background_padding)
        self.background_layout.addRow("Enable Background", self.background_enabled)
        self.background_layout.addRow("Color", self.background_color_button)
        self.background_layout.addRow("Padding", self.background_padding)
        self.details_layout.addWidget(self.background_group)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        self.details_layout.addWidget(self.remove_button)
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.details_scroll.setWidget(self.details_group)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setObjectName("annotationInspectorSplitter")
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.details_scroll)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.tree.setMinimumHeight(80)
        self.details_scroll.setMinimumHeight(80)
        self.splitter.setSizes([300, 200])
        self.layout.addWidget(self.splitter)

        self.line_width.valueChanged.connect(lambda value: self._set_style("line_width", value))
        self.extension_line_width.valueChanged.connect(lambda value: self._set_style("extension_line_width", value))
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
            self.format_group.hide()
            self.style_group.hide()
            self.layout_group.hide()
            self.background_group.hide()
            self.remove_button.hide()
            return
        if len(selected) > 1:
            self.details_message.setText(f"{len(selected)} annotations selected")
            self.details_message.show()
            self.details_form_widget.hide()
            self.format_group.hide()
            self.style_group.hide()
            self.layout_group.hide()
            self.background_group.hide()
            self.remove_button.show()
            return

        annotation = selected[0]
        self.details_message.hide()
        self.details_form_widget.show()
        self.remove_button.show()
        self.name_edit.setText(annotation.name)
        self.type_label.setText(self._item_type_name(annotation))
        self._sync_format_controls()
        self._sync_style_controls()
        self._sync_layout_controls()
        self._sync_background_controls()

    def _sync_format_controls(self) -> None:
        """Display semantic measurement format for one resolved dimension."""
        selected = self._selected_dimension_item()
        if selected is None:
            self.format_group.hide()
            return
        _annotation, dimension = selected
        self.format_group.show()
        unit_blocked = self.unit_edit.blockSignals(True)
        precision_blocked = self.precision_edit.blockSignals(True)
        try:
            self.unit_edit.setText(dimension.unit or "")
            self.precision_edit.setText(str(dimension.precision))
        finally:
            self.unit_edit.blockSignals(unit_blocked)
            self.precision_edit.blockSignals(precision_blocked)

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
            (self.extension_line_width, style.extension_line_width),
            (self.text_size, style.text_size),
            (self.arrow_size, style.arrow_size),
            (self.label_offset, style.label_offset),
        )
        for control, value in controls:
            control.blockSignals(True)
            control.setValue(value)
            control.blockSignals(False)
        self._set_color_button(style.color)

    def _sync_background_controls(self) -> None:
        """Display label-background fields for one text-bearing annotation."""
        annotation = self._selected_text_annotation()
        if annotation is None:
            self.background_group.hide()
            return
        self.background_group.show()
        enabled_blocked = self.background_enabled.blockSignals(True)
        padding_blocked = self.background_padding.blockSignals(True)
        try:
            enabled = annotation.label_background is not None
            self.background_enabled.setChecked(enabled)
            self.background_padding.setValue(annotation.label_background_padding)
            self.background_color_button.setEnabled(enabled)
            self.background_padding.setEnabled(enabled)
            self._set_background_color_button(annotation.label_background or Color.white())
        finally:
            self.background_enabled.blockSignals(enabled_blocked)
            self.background_padding.blockSignals(padding_blocked)

    def _sync_layout_controls(self) -> None:
        """Display durable spatial layout for one bound distance dimension."""
        selected = self._selected_dimension_item()
        if selected is None:
            self.layout_group.hide()
            return
        annotation, _dimension = selected
        layout = annotation.layout
        if layout is None:
            self.layout_group.hide()
            return
        self.layout_group.show()
        controls = (self.layout_offset, self.layout_normal_x, self.layout_normal_y, self.layout_normal_z)
        blocked = [control.blockSignals(True) for control in controls]
        try:
            self.layout_offset.setText(str(layout.offset))
            normal = layout.plane_normal
            values = ("", "", "") if normal is None else tuple(str(value) for value in normal)
            for control, value in zip(controls[1:], values, strict=True):
                control.setText(value)
            self.layout_status.setText(resolve_dimension_layout(annotation, self.scene).status)
        finally:
            for control, was_blocked in zip(controls, blocked, strict=True):
                control.blockSignals(was_blocked)

    def _selected_annotation(self) -> SceneAnnotation | None:
        """Return the only selected annotation entry."""
        selected = self.viewer.state.annotation_selection.objects
        return selected[0] if len(selected) == 1 else None

    def _selected_dimension(self) -> SceneAnnotation | None:
        """Return the only selected distance-dimension entry."""
        selected = self._selected_dimension_item()
        return selected[0] if selected is not None else None

    def _selected_dimension_item(self) -> tuple[SceneAnnotation, DistanceDimension] | None:
        """Return the selected entry and its resolved distance dimension."""
        annotation = self._selected_annotation()
        if annotation is None:
            return None
        try:
            item = annotation.item
            return (annotation, item) if isinstance(item, DistanceDimension) else None
        except LookupError:
            return None

    def _selected_text_annotation(self) -> SceneAnnotation | None:
        """Return the selected entry when its resolved item has label text."""
        annotation = self._selected_annotation()
        if annotation is None:
            return None
        try:
            return annotation if isinstance(annotation.item, (TextAnnotation, DistanceDimension)) else None
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

    def _commit_unit(self) -> None:
        """Commit a trimmed durable coordinate-unit declaration."""
        if self._refreshing:
            return
        selected = self._selected_dimension_item()
        if selected is None:
            return
        annotation, dimension = selected
        unit = self.unit_edit.text().strip() or None
        if unit == dimension.unit:
            self.unit_edit.setText(dimension.unit or "")
            return
        dimension.unit = unit
        self.unit_edit.setText(dimension.unit or "")
        self.viewer.refresh_annotations((annotation,))

    def _cancel_unit_edit(self) -> None:
        """Restore the durable unit and leave the editor without mutation."""
        selected = self._selected_dimension_item()
        if selected is not None:
            _annotation, dimension = selected
            blocked = self.unit_edit.blockSignals(True)
            self.unit_edit.setText(dimension.unit or "")
            self.unit_edit.blockSignals(blocked)
        self.unit_edit.clearFocus()

    def _commit_precision(self) -> None:
        """Commit one display precision from 0 to 15 inclusive."""
        if self._refreshing:
            return
        selected = self._selected_dimension_item()
        if selected is None:
            return
        annotation, dimension = selected
        try:
            precision = int(self.precision_edit.text().strip())
        except (TypeError, ValueError):
            self._restore_precision(dimension)
            return
        if not 0 <= precision <= 15:
            self._restore_precision(dimension)
            return
        if precision == dimension.precision:
            self._set_precision_text(dimension.precision)
            return
        try:
            dimension.precision = precision
        except (TypeError, ValueError):
            self._restore_precision(dimension)
            return
        self._set_precision_text(dimension.precision)
        self.viewer.refresh_annotations((annotation,))

    def _cancel_precision_edit(self) -> None:
        """Restore durable precision and leave the editor without mutation."""
        selected = self._selected_dimension_item()
        if selected is not None:
            _annotation, dimension = selected
            self._restore_precision(dimension)
            return
        self.precision_edit.clearFocus()

    def _restore_precision(self, dimension: DistanceDimension) -> None:
        """Restore the canonical durable precision and clear editor focus."""
        self._set_precision_text(dimension.precision)
        self.precision_edit.clearFocus()

    def _set_precision_text(self, precision: int) -> None:
        """Synchronize precision text without emitting editor signals."""
        blocked = self.precision_edit.blockSignals(True)
        self.precision_edit.setText(str(precision))
        self.precision_edit.blockSignals(blocked)

    def _set_style(self, name: str, value: float) -> None:
        """Set one durable dimension-style field and refresh its render layer."""
        if self._refreshing:
            return
        annotation = self._selected_dimension()
        if annotation is None or annotation.style is None:
            return
        setattr(annotation.style, name, value)
        self.viewer.refresh_annotations((annotation,))

    def _commit_layout(self) -> None:
        """Atomically replace the selected dimension's durable spatial layout."""
        if self._refreshing:
            return
        selected = self._selected_dimension_item()
        if selected is None:
            return
        annotation, _dimension = selected
        try:
            offset = float(self.layout_offset.text().strip())
            normal_text = tuple(control.text().strip() for control in (self.layout_normal_x, self.layout_normal_y, self.layout_normal_z))
            if not isfinite(offset):
                raise ValueError
            if all(not value for value in normal_text):
                normal = None
            elif all(normal_text):
                values = tuple(float(value) for value in normal_text)
                if not all(isfinite(value) for value in values):
                    raise ValueError
                normal = Vector(x=values[0], y=values[1], z=values[2])
            else:
                raise ValueError
            replacement = DistanceDimensionLayout(offset=offset, plane_normal=normal)
        except (TypeError, ValueError):
            self._sync_layout_controls()
            return
        current = annotation.layout
        if current is not None and current.offset == replacement.offset and current.plane_normal == replacement.plane_normal:
            self._sync_layout_controls()
            return
        annotation.layout = replacement
        self._sync_layout_controls()
        self.viewer.refresh_annotations((annotation,))

    def _cancel_layout_edit(self) -> None:
        """Restore the complete durable layout without mutation or refresh."""
        self._sync_layout_controls()
        for control in (self.layout_offset, self.layout_normal_x, self.layout_normal_y, self.layout_normal_z):
            control.clearFocus()

    def _reset_layout(self) -> None:
        """Reset the selected dimension to the zero-offset default layout."""
        selected = self._selected_dimension_item()
        if selected is None:
            return
        annotation, _dimension = selected
        current = annotation.layout
        if current is not None and current.offset == 0.0 and current.plane_normal is None:
            self._sync_layout_controls()
            return
        annotation.layout = DistanceDimensionLayout()
        self._sync_layout_controls()
        self.viewer.refresh_annotations((annotation,))

    def _set_background_enabled(self, enabled: bool) -> None:
        """Enable or disable the selected annotation's label background."""
        if self._refreshing:
            return
        annotation = self._selected_text_annotation()
        if annotation is None:
            return
        annotation.label_background = Color.white() if enabled else None
        self._sync_background_controls()
        self.viewer.refresh_annotations((annotation,))

    def _set_background_padding(self, value: float) -> None:
        """Set nonnegative logical-pixel label-background padding."""
        if self._refreshing:
            return
        annotation = self._selected_text_annotation()
        if annotation is None or annotation.label_background is None:
            return
        annotation.label_background_padding = value
        self.viewer.refresh_annotations((annotation,))

    def _choose_background_color(self) -> None:
        """Choose the selected annotation's label-background color."""
        annotation = self._selected_text_annotation()
        if annotation is None or annotation.label_background is None:
            return
        current = QColor.fromRgbF(*annotation.label_background.rgba)
        color = QColorDialog.getColor(
            current,
            self.widget,
            options=QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if not color.isValid():
            return
        red, green, blue, alpha = cast(tuple[int, int, int, int], color.getRgb())
        annotation.label_background = Color(red / 255, green / 255, blue / 255, alpha / 255)
        self._set_background_color_button(annotation.label_background)
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

    def _set_background_color_button(self, color: Color) -> None:
        """Display one COMPAS color, including alpha, on the background button."""
        qcolor = QColor.fromRgbF(*color.rgba)
        self.background_color_button.setText(qcolor.name(QColor.NameFormat.HexArgb))
        self.background_color_button.setStyleSheet(f"background-color: rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {qcolor.alpha()});")

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
