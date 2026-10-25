from typing import Any
from typing import cast

from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QSizePolicy

from compas_viewer.scene import ViewerSceneObject

from .booleantoggle import BooleanToggle
from .colorpicker import ColorPicker
from .component import Component
from .container import Container
from .numberedit import NumberEdit
from .textedit import TextEdit


class ObjectSetting(Container):
    """Display editable properties for the current scene selection."""

    def __init__(self) -> None:
        super().__init__(container_type="scrollable", compact=True)

    @property
    def selected(self) -> list[ViewerSceneObject]:
        """list[ViewerSceneObject]: Currently selected scene objects."""
        objects = cast(list[ViewerSceneObject], self.scene.objects)
        return [obj for obj in objects if obj.is_selected]

    def update(self) -> None:
        """Update the layout with the latest object settings."""
        if len(self.selected) == 1:
            self.populate(self.selected[0])
        elif len(self.selected) > 1:
            names = ", ".join(str(getattr(obj, "name", type(obj).__name__)) for obj in self.selected)
            types = sorted({type(getattr(obj, "item", obj)).__name__ for obj in self.selected})
            self._display_info(f"{len(self.selected)} objects selected\nTypes: {', '.join(types)}\nNames: {names}")
        else:
            self.display_text("No object selected")

    def populate(self, obj: ViewerSceneObject) -> None:
        """Populate controls for a selected scene object.

        Parameters
        ----------
        obj
            Scene object whose editable properties should be displayed.

        """

        dynamic_obj = cast(Any, obj)

        item = obj.data
        parameter_lines = []
        for name, parameter in obj.parameter_info.items():
            if parameter.available:
                value = repr(parameter.value)
                if len(value) > 80:
                    value = f"{value[:77]}..."
            else:
                value = "<not exposed by object>"
            parameter_lines.append(f"  {name}: {value}")
        parameters = "\nParameters:\n" + "\n".join(parameter_lines) if parameter_lines else ""
        self._display_info(f"Name: {getattr(obj, 'name', type(obj).__name__)}\nType: {type(item).__name__}\nVisible: {obj.show}{parameters}")

        def _update_obj_settings(*arg: object) -> None:
            obj.update(update_data=True)
            self.viewer.renderer.update()

        def _update_sceneform(*arg: object) -> None:
            self.viewer.ui.sidebar.sceneform.update(refresh=True)

        if hasattr(obj, "name"):
            name_edit = TextEdit(obj, "name", action=_update_sceneform)
            self._add_control(name_edit)

        if hasattr(obj, "show_points"):
            self._add_control(BooleanToggle(obj=obj, attr="show_points", action=_update_obj_settings))

        if hasattr(obj, "show_lines"):
            self._add_control(BooleanToggle(obj=obj, attr="show_lines", action=_update_obj_settings))

        if hasattr(obj, "show_faces"):
            self._add_control(BooleanToggle(obj=obj, attr="show_faces", action=_update_obj_settings))

        if hasattr(dynamic_obj, "pointcolor") and dynamic_obj.pointcolor is not None:
            self._add_control(ColorPicker(obj=cast(Any, obj), attr="pointcolor", action=_update_obj_settings))

        if hasattr(dynamic_obj, "linecolor") and dynamic_obj.linecolor is not None:
            self._add_control(ColorPicker(obj=cast(Any, obj), attr="linecolor", action=_update_obj_settings))

        if hasattr(dynamic_obj, "facecolor") and dynamic_obj.facecolor is not None:
            self._add_control(ColorPicker(obj=cast(Any, obj), attr="facecolor", action=_update_obj_settings))

        if hasattr(obj, "linewidth"):
            linewidth_edit = NumberEdit(obj, "linewidth", title="line width", min_val=0.0, max_val=10.0, action=_update_obj_settings)
            self._add_control(linewidth_edit)

        if hasattr(obj, "pointsize"):
            pointsize_edit = NumberEdit(obj, "pointsize", title="point size", min_val=0.0, max_val=10.0, action=_update_obj_settings)
            self._add_control(pointsize_edit)

        if hasattr(obj, "opacity"):
            opacity_edit = NumberEdit(obj, "opacity", title="opacity", min_val=0.0, max_val=1.0, action=_update_obj_settings)
            self._add_control(opacity_edit)

    def _display_info(self, text: str) -> None:
        """Display selection information in a bounded, scrollable panel.

        Parameters
        ----------
        text
            Selection information to display.
        """
        self.reset()
        info = QPlainTextEdit()
        info.setObjectName("objectInfo")
        info.setReadOnly(True)
        info.setPlainText(text)
        info.setMinimumHeight(72)
        info.setMaximumHeight(150)
        info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info.setStyleSheet("QPlainTextEdit#objectInfo { padding: 4px; }")
        assert self.layout is not None
        self.layout.addWidget(info)

    def _add_control(self, control: Component) -> None:
        """Add a compact control row to the object inspector.

        Parameters
        ----------
        control
            Bound component containing a horizontal control layout.

        """
        self.add(control)
