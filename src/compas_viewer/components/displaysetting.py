from collections.abc import Callable
from types import SimpleNamespace
from typing import TYPE_CHECKING
from typing import Any

from .booleantoggle import BooleanToggle
from .boundcomponent import BoundComponent
from .choiceedit import ChoiceEdit
from .colorpicker import ColorPicker
from .container import Container
from .numberedit import NumberEdit

if TYPE_CHECKING:
    from .viewport import ViewPort


class DisplaySetting(Container):
    """Edit viewport, grid, and color settings with live feedback."""

    def __init__(self, viewport: "ViewPort") -> None:
        super().__init__(container_type="scrollable", compact=True)
        self.viewport = viewport
        self.renderer = viewport.renderer
        dx, nx, dy, ny = self.viewer.config.renderer.gridsize
        self.grid = SimpleNamespace(dx=dx, nx=float(nx), dy=dy, ny=float(ny))
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

        def update_grid(*args: object) -> None:
            self.viewer.state.set("renderer.gridsize", (self.grid.dx, int(self.grid.nx), self.grid.dy, int(self.grid.ny)))

        def update_unit(*args: object) -> None:
            dx, nx, dy, ny = renderer_config.gridsize
            self.grid.dx = dx
            self.grid.nx = float(nx)
            self.grid.dy = dy
            self.grid.ny = float(ny)

        def add_state_control(path: str, control: BoundComponent[Any]) -> None:
            self._state_controls[path] = control
            self.add(control)

        add_state_control("unit", ChoiceEdit(self.viewport, "unit", ["m", "cm", "mm"], title="Units", action=update_unit))
        add_state_control("renderer.rendermode", ChoiceEdit(self.renderer, "rendermode", ["shaded", "lighted", "ghosted", "wireframe"], title="Render Mode"))
        add_state_control("renderer.view", ChoiceEdit(self.renderer, "view", ["perspective", "top", "front", "right", "ortho"], title="View"))
        add_state_control("renderer.backgroundcolor", ColorPicker(renderer_config, "backgroundcolor", title="Background", action=notify("renderer.backgroundcolor")))
        add_state_control("renderer.selectioncolor", ColorPicker(renderer_config, "selectioncolor", title="Selection", action=notify("renderer.selectioncolor")))
        add_state_control("renderer.show_grid", BooleanToggle(renderer_config, "show_grid", title="Show Grid", action=notify("renderer.show_grid")))
        add_state_control("renderer.show_gridz", BooleanToggle(renderer_config, "show_gridz", title="Show Z Axis", action=notify("renderer.show_gridz")))
        add_state_control("renderer.gridmode", ChoiceEdit(renderer_config, "gridmode", ["full", "quadrant"], title="Grid Mode", action=notify("renderer.gridmode")))
        add_state_control("renderer.gridcolor", ColorPicker(renderer_config, "gridcolor", title="Grid Color", action=notify("renderer.gridcolor")))
        self.add(NumberEdit(self.grid, "dx", title="Grid X Extent", min_val=0.001, max_val=1e9, action=update_grid))
        self.add(NumberEdit(self.grid, "nx", title="Grid X Divisions", min_val=1, max_val=1000, step=1, decimals=0, action=update_grid))
        self.add(NumberEdit(self.grid, "dy", title="Grid Y Extent", min_val=0.001, max_val=1e9, action=update_grid))
        self.add(NumberEdit(self.grid, "ny", title="Grid Y Divisions", min_val=1, max_val=1000, step=1, decimals=0, action=update_grid))

    def _on_state_changed(self, path: str, value: object) -> None:
        """Synchronize local form models with global viewer state."""
        if path == "renderer.gridsize":
            dx, nx, dy, ny = self.viewer.config.renderer.gridsize
            self.grid.dx = dx
            self.grid.nx = float(nx)
            self.grid.dy = dy
            self.grid.ny = float(ny)
        elif control := self._state_controls.get(path):
            control.sync_from_bound_object(value)
