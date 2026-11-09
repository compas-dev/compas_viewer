from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any

from .boundcomponent import BoundComponent
from .choiceedit import ChoiceEdit
from .colorpicker import ColorPicker
from .container import Container

if TYPE_CHECKING:
    from .viewport import ViewPort


class DisplaySetting(Container):
    """Edit viewport presentation settings with live feedback."""

    def __init__(self, viewport: "ViewPort") -> None:
        super().__init__(container_type="scrollable", compact=True)
        self.viewport = viewport
        self.renderer = viewport.renderer
        self._state_controls: dict[str, BoundComponent[Any]] = {}
        self.viewer.state.changed.connect(self._on_state_changed)
        self.populate()

    def populate(self) -> None:
        """Populate the display settings form."""
        renderer_config = self.viewer.config.renderer

        def notify(path: str) -> Callable[..., None]:
            def publish(*args: object) -> None:
                self.viewer.state.notify(path)

            return publish

        def add_state_control(path: str, control: BoundComponent[Any]) -> None:
            self._state_controls[path] = control
            self.add(control)

        add_state_control("renderer.rendermode", ChoiceEdit(self.renderer, "rendermode", ["shaded", "lighted", "ghosted", "wireframe"], title="Render Mode"))
        add_state_control("renderer.view", ChoiceEdit(self.renderer, "view", ["perspective", "top", "front", "right", "ortho"], title="View"))
        add_state_control("renderer.backgroundcolor", ColorPicker(renderer_config, "backgroundcolor", title="Background", action=notify("renderer.backgroundcolor")))
        add_state_control("renderer.selectioncolor", ColorPicker(renderer_config, "selectioncolor", title="Selection", action=notify("renderer.selectioncolor")))

    def _on_state_changed(self, path: str, value: object) -> None:
        """Synchronize local form models with global viewer state."""
        if control := self._state_controls.get(path):
            control.sync_from_bound_object(value)
