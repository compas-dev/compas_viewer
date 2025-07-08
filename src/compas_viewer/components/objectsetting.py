from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .container import Container
from compas_viewer.components.booleantoggle import BooleanToggle
from compas_viewer.components.colorpicker import ColorPicker
from compas_viewer.components.component import Component
from compas_viewer.components.numberedit import NumberEdit
from compas_viewer.components.textedit import TextEdit

from compas_viewer.scene import ViewerSceneObject


class ObjectSetting(Container):
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
        if len(self.selected) == 1:
            self.populate(self.selected[0])
        elif len(self.selected) > 1:
            self.display_text("Multiple objects selected")
        else:
            self.display_text("No object selected")

    def populate(self, obj: ViewerSceneObject) -> None:
        """Populate the layout with the settings of the selected object."""

        self.reset()

        def _update_obj_settings(*arg):
            obj.update()
            self.viewer.renderer.update()

        def _update_obj_settings(*arg):
            obj.update(update_data=True)
            self.viewer.renderer.update()

        def _update_sceneform(*arg):
            self.viewer.ui.sidebar.sceneform.update(refresh=True)

        if hasattr(obj, "name"):
            name_edit = TextEdit(obj, "name", callback=_update_sceneform)
            self.add(name_edit)

        if hasattr(obj, "show_points"):
            self.add(BooleanToggle(obj=obj, attr="show_points", callback=_update_obj_settings))

        if hasattr(obj, "show_lines"):
            self.add(BooleanToggle(obj=obj, attr="show_lines", callback=_update_obj_settings))

        if hasattr(obj, "show_faces"):
            self.add(BooleanToggle(obj=obj, attr="show_faces", callback=_update_obj_settings))

        if hasattr(obj, "pointcolor"):
            self.add(ColorPicker(obj=obj, attr="pointcolor", callback=_update_obj_settings))

        if hasattr(obj, "linecolor"):
            self.add(ColorPicker(obj=obj, attr="linecolor", callback=_update_obj_settings))

        if hasattr(obj, "facecolor"):
            self.add(ColorPicker(obj=obj, attr="facecolor", callback=_update_obj_settings))

        if hasattr(obj, "linewidth"):
            linewidth_edit = NumberEdit(obj, "linewidth", title="line width", min_val=0.0, max_val=10.0, callback=_update_obj_settings)
            self.add(linewidth_edit)

        if hasattr(obj, "pointsize"):
            pointsize_edit = NumberEdit(obj, "pointsize", title="point size", min_val=0.0, max_val=10.0, callback=_update_obj_settings)
            self.add(pointsize_edit)

        if hasattr(obj, "opacity"):
            opacity_edit = NumberEdit(obj, "opacity", title="opacity", min_val=0.0, max_val=1.0, callback=_update_obj_settings)
            self.add(opacity_edit)
