from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.components.color import ColorDialog
from compas_viewer.components.component import Component
from compas_viewer.components.numberedit import NumberEdit
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

    @property
    def selected(self):
        return [obj for obj in self.scene.objects if obj.is_selected]

    def reset(self):
        """Reset the content widget and layout to a clean state."""
        self.children = []
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.widget.setWidget(self.scroll_content)
        self.settings_layout = QVBoxLayout()
        self.settings_layout.setSpacing(0)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.addLayout(self.settings_layout)

    def update(self):
        """Update the layout with the latest object settings."""
        self.reset()

        if len(self.selected) == 1:
            self._populate(self.selected[0])
            # self._add_event_listeners()
        elif len(self.selected) > 1:
            self._add_row("Multiple objects selected")
        else:
            self._add_row("No object selected")

    def _populate(self, obj: object) -> None:
        """Populate the layout with the settings of the selected object."""

        def update_obj(_, value):
            obj.update()
            self.viewer.renderer.update()
            self.viewer.ui.sidebar.sceneform.update(refresh=True)


        # if hasattr(obj, "pointcolor") and obj.pointcolor is not None:
        #     self._add_row("pointcolor", ColorDialog(obj=obj, attr="pointcolor"))

        # if hasattr(obj, "linecolor") and obj.linecolor is not None:
        #     self._add_row("linecolor", ColorDialog(obj=obj, attr="linecolor"))

        # if hasattr(obj, "facecolor") and obj.facecolor is not None:
        #     self._add_row("facecolor", ColorDialog(obj=obj, attr="facecolor"))

        if hasattr(obj, "name") and obj.name is not None:
            name_edit = TextEdit(obj, "name", callback=update_obj)
            self.add(name_edit)

        if hasattr(obj, "linewidth") and obj.linewidth is not None:
            linewidth_edit = NumberEdit(obj, "linewidth", title="line width", min_val=0.0, max_val=10.0, callback=update_obj)
            self.add(linewidth_edit)

        if hasattr(obj, "pointsize") and obj.pointsize is not None:
            pointsize_edit = NumberEdit(obj, "pointsize", title="point size", min_val=0.0, max_val=10.0, callback=update_obj)
            self.add(pointsize_edit)

        if hasattr(obj, "opacity") and obj.opacity is not None:
            opacity_edit = NumberEdit(obj, "opacity", title="opacity", min_val=0.0, max_val=1.0, callback=update_obj)
            self.add(opacity_edit)

    def add(self, component: Component) -> None:
        self.settings_layout.addWidget(component.widget)
        self.children.append(component)

    def _add_row(self, attr_name: str, widget: QWidget = None) -> None:
        """Create a setting row with label and widget, then add it to the layout."""
        row_layout = QHBoxLayout()
        row_layout.setSpacing(0)
        row_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(attr_name)
        row_layout.addWidget(label)

        if widget:
            row_layout.addWidget(widget)
            self.children.append(widget)

        self.settings_layout.addLayout(row_layout)
