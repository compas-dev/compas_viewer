from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QSizePolicy

from compas.colors import Color
from compas.colors import ColorDict
from compas.scene import SceneItemNotBoundError
from compas.scene import SceneObject
from compas_viewer.forms import scene_editable_attributes
from compas_viewer.scene.parameters import inspect_object_parameters

from .booleantoggle import BooleanToggle
from .colorpicker import ColorPicker
from .component import Component
from .container import Container
from .numberedit import NumberEdit
from .textedit import TextEdit


@dataclass(slots=True)
class _EditableAttributeBinding:
    """Bind a control to one contextual stable scene-object attribute."""

    sceneobject: SceneObject
    name: str
    update: Callable[[SceneObject, object], None] | None

    @property
    def value(self) -> object:
        """Return the current attribute value."""
        return getattr(self.sceneobject, self.name)

    @value.setter
    def value(self, value: object) -> None:
        """Update the attribute and restore its prior value on failure."""
        previous = _snapshot_value(self.value)
        if isinstance(previous, int) and not isinstance(previous, bool) and isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Editable integer attribute {self.name} requires a whole number.")
            value = int(value)
        try:
            if self.update is None:
                setattr(self.sceneobject, self.name, value)
            else:
                self.update(self.sceneobject, value)
        except Exception:
            try:
                setattr(self.sceneobject, self.name, previous)
            except Exception:
                pass
            raise


def _snapshot_value(value: object) -> object:
    """Copy mutable color mappings for transactional control rollback."""
    if isinstance(value, ColorDict):
        snapshot = ColorDict(value.default)
        snapshot.update(value)
        return snapshot
    return value


class ObjectSetting(Container):
    """Display editable properties for the current scene selection."""

    def __init__(self) -> None:
        super().__init__(container_type="scrollable", compact=True)

    @property
    def selected(self) -> list[SceneObject]:
        """list[SceneObject]: Currently selected stable scene objects."""
        return [obj for obj in self.scene.objects if self.scene.is_selected(obj)]

    def update(self) -> None:
        """Update the layout with the latest object settings."""
        if len(self.selected) == 1:
            self.populate(self.selected[0])
        elif len(self.selected) > 1:
            names = ", ".join(str(obj.name) for obj in self.selected)
            types = sorted({self._item_type_name(obj) for obj in self.selected})
            self._display_info(f"{len(self.selected)} objects selected\nTypes: {', '.join(types)}\nNames: {names}")
        else:
            self.display_text("No object selected")

    def populate(self, obj: SceneObject) -> None:
        """Populate controls for a selected scene object.

        Parameters
        ----------
        obj
            Scene object whose editable properties should be displayed.

        """
        try:
            item = obj.item
        except SceneItemNotBoundError:
            item = None
        parameter_lines = []
        for name, parameter in inspect_object_parameters(item).items():
            if parameter.available:
                value = repr(parameter.value)
                if len(value) > 80:
                    value = f"{value[:77]}..."
            else:
                value = "<not exposed by object>"
            parameter_lines.append(f"  {name}: {value}")
        parameters = "\nParameters:\n" + "\n".join(parameter_lines) if parameter_lines else ""
        item_type = type(item).__name__ if item is not None else "Unresolved"
        controls = []
        for name, callback in scene_editable_attributes("Viewer", obj).items():
            control = self._create_control(_EditableAttributeBinding(obj, name, callback))
            if control is not None:
                controls.append(control)
        self._display_info(f"Name: {obj.name}\nType: {item_type}\nVisible: {obj.show}{parameters}")
        for control in controls:
            self.add(control)

    def _create_control(self, binding: _EditableAttributeBinding) -> Component | None:
        """Create a control inferred from the current attribute value."""
        value = binding.value
        title = binding.name.replace("_", " ").capitalize()

        def refresh(*args: object) -> None:
            self._refresh_object(binding.sceneobject)

        if isinstance(value, bool):
            return BooleanToggle(binding, "value", title=title, action=refresh)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return NumberEdit(binding, "value", title=title, action=refresh)
        if isinstance(value, str):
            return TextEdit(binding, "value", title=title, action=refresh)
        if isinstance(value, (Color, ColorDict)):
            return ColorPicker(binding, "value", title=title, action=refresh)
        return None

    def _refresh_object(self, sceneobject: SceneObject) -> None:
        """Conservatively rebuild render data and refresh Viewer UI."""
        self.scene.render_object(sceneobject).update(update_data=True)
        self.viewer.renderer.update()
        self.viewer.ui.sidebar.sceneform.update(refresh=True)
        self.update()

    def _item_type_name(self, sceneobject: SceneObject) -> str:
        """Return the represented type name without resolving external data."""
        try:
            item = sceneobject.item
        except SceneItemNotBoundError:
            return "Unresolved"
        return type(item).__name__ if item is not None else "None"

    def _display_info(self, text: str) -> None:
        """Display selection information in a bounded, scrollable panel."""
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
