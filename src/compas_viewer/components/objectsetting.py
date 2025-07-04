from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.components.color import ColorDialog
from compas_viewer.components.component import Component
from compas_viewer.components.double_edit import DoubleEdit
from compas_viewer.components.textedit import TextEdit


class ObjectSetting(Component):
    """
    A component to manage the settings of objects in the viewer.
    """

    def __init__(self):
        super().__init__()
        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)
        self.reset()

    def reset(self):
        """Reset the content widget and layout to a clean state."""
        self.sub_widgets = {}
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.widget.setWidget(self.scroll_content)
        self.settings_layout = QVBoxLayout()
        self.settings_layout.setSpacing(0)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.addLayout(self.settings_layout)

    @property
    def selected(self):
        return [obj for obj in self.scene.objects if obj.is_selected]

    def add_row(self, attr_name: str, widget: QWidget = None) -> None:
        """Create a setting row with label and widget, then add it to the layout."""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(0)
        row_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(attr_name)
        row_layout.addWidget(label)

        if widget:
            row_layout.addWidget(widget)
            self.sub_widgets[attr_name] = widget

        self.settings_layout.addLayout(row_layout)

    def populate(self) -> None:
        """Populate the layout with the settings of the selected object."""
        obj = self.selected[0]

        if not obj:
            return

        self.add_row("name", TextEdit(text=str(obj.name)))

        if hasattr(obj, "pointcolor") and obj.pointcolor is not None:
            self.add_row("pointcolor", ColorDialog(obj=obj, attr="pointcolor"))

        if hasattr(obj, "linecolor") and obj.linecolor is not None:
            self.add_row("linecolor", ColorDialog(obj=obj, attr="linecolor"))

        if hasattr(obj, "facecolor") and obj.facecolor is not None:
            self.add_row("facecolor", ColorDialog(obj=obj, attr="facecolor"))

        if hasattr(obj, "linewidth") and obj.linewidth is not None:
            self.add_row("linewidth", DoubleEdit(title=None, value=obj.linewidth, min_val=0.0, max_val=10.0))

        if hasattr(obj, "pointsize") and obj.pointsize is not None:
            self.add_row("pointsize", DoubleEdit(title=None, value=obj.pointsize, min_val=0.0, max_val=10.0))

        if hasattr(obj, "opacity") and obj.opacity is not None:
            self.add_row("opacity", DoubleEdit(title=None, value=obj.opacity, min_val=0.0, max_val=1.0))

    def update(self):
        """Update the layout with the latest object settings."""
        self.reset()

        if len(self.selected) == 1:
            self.populate()
            self._add_event_listeners()
        elif len(self.selected) > 1:
            self.add_row("Multiple objects selected")
        else:
            self.add_row("No object selected")

    def _add_event_listeners(self):
        """Add event listeners to the sub widgets."""

        def _update_obj():
            if len(self.selected) == 0:
                return

            obj = self.selected[0]

            for attr_name, widget in self.sub_widgets.items():
                if not hasattr(obj, attr_name):
                    continue
                if isinstance(widget, TextEdit):
                    value = widget.text_edit.toPlainText()
                elif isinstance(widget, DoubleEdit):
                    value = widget.spinbox.value()
                else:
                    continue

                setattr(obj, attr_name, value)

            obj.update()

        for widget in self.sub_widgets.values():
            if isinstance(widget, TextEdit):
                widget.text_edit.textChanged.connect(_update_obj)
            elif isinstance(widget, DoubleEdit):
                widget.spinbox.valueChanged.connect(_update_obj)
