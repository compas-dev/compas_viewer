from types import SimpleNamespace

from compas.colors import Color
from compas_viewer.components.viewport import ViewPort
from compas_viewer.state import ViewerState
from compas_viewer.config import Config
from compas_viewer.uidefinitions import default_sidebar_items
from compas_viewer.scene.gridobject import GridObject


class Renderer:
    def __init__(self):
        self.camera = SimpleNamespace(scale=1.0, distance=10.0)
        self.grid_rebuilds = 0
        self.updates = 0

    def rebuild_grid(self):
        self.grid_rebuilds += 1

    def update(self):
        self.updates += 1


def test_unit_can_change_while_viewer_is_running():
    renderer = Renderer()
    config = Config()
    viewer = SimpleNamespace(config=config, state=ViewerState(config), running=True)
    viewport = SimpleNamespace(_unit="m", renderer=renderer, viewer=viewer)

    ViewPort.unit.fset(viewport, "cm")

    assert viewport._unit == "cm"
    assert config.unit == "cm"
    assert config.renderer.gridsize == (1000.0, 10, 1000.0, 10)
    assert renderer.camera.scale == 100.0
    assert renderer.camera.distance == 1000.0
    assert renderer.grid_rebuilds == 1
    assert renderer.updates == 1


def test_grid_supports_positive_odd_division_counts():
    grid = GridObject(framesize=(10.0, 7, 5.0, 3), linecolor=Color.grey())

    assert grid.nx == 7
    assert grid.ny == 3


def test_default_sidebar_contains_display_settings():
    item_types = [item["type"] for item in default_sidebar_items()]

    assert "DisplaySetting" in item_types
