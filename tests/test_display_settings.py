from compas.colors import Color
from compas_viewer.scene.gridobject import GridObject
from compas_viewer.uidefinitions import default_sidebar_items


def test_grid_supports_positive_odd_division_counts():
    grid = GridObject(framesize=(10.0, 7, 5.0, 3), linecolor=Color.grey())

    assert grid.nx == 7
    assert grid.ny == 3


def test_default_sidebar_contains_display_settings():
    item_types = [item["type"] for item in default_sidebar_items()]

    assert "DisplaySetting" in item_types
