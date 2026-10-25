import pytest

from compas.colors import Color
from compas_viewer import config


def test_config_dict_roundtrip_preserves_nested_types_and_colors():
    original = config.Config()
    original.window.width = 1440
    original.renderer.backgroundcolor = Color(0.1, 0.2, 0.3, 0.4)
    original.renderer.gridsize = (25.0, 5, 50.0, 10)

    restored = config.Config.from_dict(original.to_dict())

    assert isinstance(restored.window, config.WindowConfig)
    assert isinstance(restored.renderer, config.RendererConfig)
    assert restored.window.width == 1440
    assert restored.renderer.backgroundcolor == original.renderer.backgroundcolor
    assert restored.renderer.gridsize == (25.0, 5, 50.0, 10)
    assert restored.schema_version == 1


def test_config_json_roundtrip_omits_runtime_callbacks(tmp_path):
    filepath = tmp_path / "viewer.json"
    original = config.Config()

    original.to_json(filepath)
    restored = config.Config.from_json(filepath)

    assert "commands" not in original.to_dict()
    assert "items" not in original.to_dict()["ui"]["menubar"]
    assert restored.renderer.selectioncolor == original.renderer.selectioncolor


def test_legacy_ui_display_settings_are_migrated_to_root():
    restored = config.Config.from_dict({"ui": {"display": {"pointsize": 12.0}}})

    assert restored.schema_version == 1
    assert restored.display.pointsize == 12.0


def test_newer_config_schema_is_rejected():
    with pytest.raises(ValueError, match="schema version"):
        config.Config.from_dict({"schema_version": 2})


def test_default_appearance_follows_system():
    assert config.Config().ui.appearance == "system"


def test_view_menu_contains_all_appearance_modes():
    from compas_viewer.uidefinitions import default_menu_items

    view_menu = next(item for item in default_menu_items() if item["title"] == "View")
    appearance_menu = next(item for item in view_menu["items"] if item.get("title") == "Appearance")

    assert appearance_menu["type"] == "group"
    assert [item["title"] for item in appearance_menu["items"]] == ["System", "Light", "Dark"]
