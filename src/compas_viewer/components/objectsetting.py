from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.components.booleantoggle import BooleanToggle
from compas_viewer.components.colorpicker import ColorPicker
from compas_viewer.components.component import Component
from compas_viewer.components.numberedit import NumberEdit
from compas_viewer.components.textedit import TextEdit

from compas_viewer.scene import ViewerSceneObject


class ObjectSetting(Component):
    """
    A component to manage the settings of objects in the viewer.
    """

    def __init__(self):
        super().__init__(scrollable=True)

    @property
    def selected(self):
        return [obj for obj in self.scene.objects if obj.is_selected]

    def update(self):
        """Update the layout with the latest object settings."""
        self.reset()

        if len(self.selected) == 1:
            self.populate(self.selected[0])
        elif len(self.selected) > 1:
            self.add_label("Multiple objects selected")
        else:
            self.add_label("No object selected")

    def populate(self, obj: ViewerSceneObject) -> None:
        """Populate the layout with the settings of the selected object."""

        def update_obj_settings(*arg):
            obj.update()
            self.viewer.renderer.update()

        def update_obj_color(*arg):
            obj.update(update_data=True)
            self.viewer.renderer.update()

        def update_sceneform(*arg):
            self.viewer.ui.sidebar.sceneform.update(refresh=True)

        if hasattr(obj, "name") and obj.name is not None:
            name_edit = TextEdit(obj, "name", callback=update_sceneform)
            self.add(name_edit)

        if hasattr(obj, "show_points") and obj.show_points is not None:
            self.add(BooleanToggle(obj=obj, attr="show_points", callback=update_obj_settings))

        if hasattr(obj, "show_lines") and obj.show_lines is not None:
            self.add(BooleanToggle(obj=obj, attr="show_lines", callback=update_obj_settings))

        if hasattr(obj, "show_faces") and obj.show_faces is not None:
            self.add(BooleanToggle(obj=obj, attr="show_faces", callback=update_obj_settings))

        if hasattr(obj, "pointcolor") and obj.pointcolor is not None:
            self.add(ColorPicker(obj=obj, attr="pointcolor", callback=update_obj_color))

        if hasattr(obj, "linecolor") and obj.linecolor is not None:
            self.add(ColorPicker(obj=obj, attr="linecolor", callback=update_obj_color))

        if hasattr(obj, "facecolor") and obj.facecolor is not None:
            self.add(ColorPicker(obj=obj, attr="facecolor", callback=update_obj_color))

        if hasattr(obj, "linewidth") and obj.linewidth is not None:
            linewidth_edit = NumberEdit(obj, "linewidth", title="line width", min_val=0.0, max_val=10.0, callback=update_obj_settings)
            self.add(linewidth_edit)

        if hasattr(obj, "pointsize") and obj.pointsize is not None:
            pointsize_edit = NumberEdit(obj, "pointsize", title="point size", min_val=0.0, max_val=10.0, callback=update_obj_settings)
            self.add(pointsize_edit)

        if hasattr(obj, "opacity") and obj.opacity is not None:
            opacity_edit = NumberEdit(obj, "opacity", title="opacity", min_val=0.0, max_val=1.0, callback=update_obj_settings)
            self.add(opacity_edit)

    def add_label(self, text: str) -> None:
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: gray; font-style: italic; padding: 10px;")
        self.layout.addWidget(label)
