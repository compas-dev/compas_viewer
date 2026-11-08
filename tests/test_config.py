import re
from dataclasses import dataclass
from dataclasses import field

import pytest

from compas.colors import Color
from compas_viewer import config


def test_config_dict_roundtrip_preserves_nested_types_and_colors(tmp_path):
    original = config.Config()
    icon = tmp_path / "viewer-icon.png"
    icon.write_bytes(b"icon")
    original.window.icon = str(icon)
    original.window.width = 1440
    original.renderer.backgroundcolor = Color(0.1, 0.2, 0.3, 0.4)
    original.renderer.gridsize = (25.0, 5, 50.0, 10)

    restored = config.Config.from_dict(original.to_dict())

    assert isinstance(restored.window, config.WindowConfig)
    assert isinstance(restored.renderer, config.RendererConfig)
    assert restored.window.icon == str(icon)
    assert restored.window.width == 1440
    assert restored.renderer.backgroundcolor == original.renderer.backgroundcolor
    assert restored.renderer.gridsize == (25.0, 5, 50.0, 10)
    assert restored.schema_version == 2


def test_config_json_roundtrip_uses_declared_fields_only(tmp_path):
    filepath = tmp_path / "viewer.json"
    original = config.Config()
    original.runtime_only = "ignored"
    original.ui.runtime_only = "ignored"

    original.to_json(filepath)
    restored = config.Config.from_json(filepath)

    assert "runtime_only" not in original.to_dict()
    assert "runtime_only" not in original.to_dict()["ui"]
    assert restored.renderer.selectioncolor == original.renderer.selectioncolor


def test_schema_one_config_drops_retired_fields_and_preserves_retained_values():
    restored = config.Config.from_dict(
        {
            "schema_version": 1,
            "unit": "mm",
            "display": {"pointsize": 12.0},
            "commands": {"legacy": "callback"},
            "window": {"title": "Legacy Viewer", "about": "Legacy about", "fullscreen": True},
            "renderer": {"opacity": 0.5, "view": "top"},
            "ui": {
                "view3d": {"show": True},
                "display": {"pointsize": 12.0},
                "toolbar": {"show": True, "items": []},
                "sidebar": {"width": 400, "show_widgets": False, "sceneform": False},
            },
        }
    )

    assert restored.schema_version == 2
    assert restored.window.title == "Legacy Viewer"
    assert restored.window.fullscreen is True
    assert restored.renderer.view == "top"
    assert restored.ui.toolbar.show is True
    assert restored.ui.sidebar.width == 400
    assert "unit" not in restored.to_dict()
    assert "display" not in restored.to_dict()


@pytest.mark.parametrize(
    "data, path",
    [
        ({"schema_version": 1, "unknown": True}, "unknown"),
        ({"schema_version": 1, "renderer": {"unknown": True}}, "renderer.unknown"),
        ({"schema_version": 2, "unit": "m"}, "unit"),
        ({"schema_version": 2, "display": {}}, "display"),
        ({"schema_version": 2, "window": {"about": "old"}}, "window.about"),
        ({"schema_version": 2, "renderer": {"opacity": 1.0}}, "renderer.opacity"),
        ({"schema_version": 2, "ui": {"sidebar": {"sceneform": True}}}, "ui.sidebar.sceneform"),
        ({"schema_version": 2, "ui": {"sidebar": {"show_widgets": True}}}, "ui.sidebar.show_widgets"),
    ],
)
def test_config_rejects_unknown_or_retired_fields(data, path):
    with pytest.raises(ValueError, match=path.replace(".", r"\.")):
        config.Config.from_dict(data)


@pytest.mark.parametrize("version", [-1, 3, "2", True])
def test_unsupported_config_schema_is_rejected(version):
    with pytest.raises(ValueError, match="schema version"):
        config.Config.from_dict({"schema_version": version})


@pytest.mark.parametrize(
    "data, error, path",
    [
        ({"schema_version": 2, "window": {"width": 0}}, ValueError, "window.width"),
        ({"schema_version": 2, "window": {"height": 1.5}}, TypeError, "window.height"),
        ({"schema_version": 2, "ui": {"appearance": "sepia"}}, ValueError, "ui.appearance"),
        ({"schema_version": 2, "renderer": {"gridmode": "half"}}, ValueError, "renderer.gridmode"),
        ({"schema_version": 2, "renderer": {"gridsize": [10.0, 10]}}, ValueError, "renderer.gridsize"),
        ({"schema_version": 2, "renderer": {"ghostopacity": 1.1}}, ValueError, "renderer.ghostopacity"),
        ({"schema_version": 2, "camera": {"position": [0.0, 0.0]}}, ValueError, "camera.position"),
        ({"schema_version": 2, "camera": {"near": 10.0, "far": 1.0}}, ValueError, "camera.far"),
        ({"schema_version": 2, "vectorsize": 0.0}, ValueError, "vectorsize"),
    ],
)
def test_config_validation_reports_full_paths(data, error, path):
    with pytest.raises(error, match=path.replace(".", r"\.")):
        config.Config.from_dict(data)


@pytest.mark.parametrize(
    "data, path",
    [
        ({"schema_version": 2, "vectorsize": float("nan")}, "vectorsize"),
        ({"schema_version": 2, "vectorsize": float("inf")}, "vectorsize"),
        ({"schema_version": 2, "camera": {"near": float("nan")}}, "camera.near"),
        ({"schema_version": 2, "camera": {"far": float("-inf")}}, "camera.far"),
        ({"schema_version": 2, "renderer": {"gridsize": [float("inf"), 10, 10.0, 10]}}, "renderer.gridsize[0]"),
        ({"schema_version": 2, "renderer": {"gridsize": [10.0, 10, float("nan"), 10]}}, "renderer.gridsize[2]"),
        (
            {
                "schema_version": 2,
                "renderer": {"backgroundcolor": {"__color__": [0.0, float("nan"), 0.0, 1.0]}},
            },
            "renderer.backgroundcolor[1]",
        ),
    ],
)
def test_config_rejects_nonfinite_numbers_with_full_paths(data, path):
    with pytest.raises(ValueError, match=rf"{re.escape(path)}.*finite"):
        config.Config.from_dict(data)


def test_renderer_accepts_orthographic_view():
    restored = config.Config.from_dict({"schema_version": 2, "renderer": {"view": "ortho"}})

    assert restored.renderer.view == "ortho"


@dataclass
class ExtensionConfig(config.ConfigBase):
    enabled: bool = False

    def validate(self, path: str = "extension") -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError(f"{path}.enabled should be a boolean.")


@dataclass
class ExtendedConfig(config.Config):
    extension: ExtensionConfig = field(default_factory=ExtensionConfig)


def test_typed_config_subclass_roundtrips_and_validates_nested_section():
    original = ExtendedConfig(extension=ExtensionConfig(enabled=True))

    restored = ExtendedConfig.from_dict(original.to_dict())

    assert isinstance(restored, ExtendedConfig)
    assert isinstance(restored.extension, ExtensionConfig)
    assert restored.extension.enabled is True

    with pytest.raises(TypeError, match=r"extension\.enabled"):
        ExtendedConfig.from_dict({"schema_version": 2, "extension": {"enabled": "yes"}})

    invalid = ExtendedConfig()
    setattr(invalid, "extension", "invalid")
    with pytest.raises(TypeError, match=r"extension.*ExtensionConfig"):
        invalid.validate()


def test_default_appearance_follows_system():
    assert config.Config().ui.appearance == "system"


def test_view_menu_contains_all_appearance_modes():
    from compas_viewer.uidefinitions import default_menu_items

    view_menu = next(item for item in default_menu_items() if item["title"] == "View")
    appearance_menu = next(item for item in view_menu["items"] if item.get("title") == "Appearance")

    assert appearance_menu["type"] == "group"
    assert [item["title"] for item in appearance_menu["items"]] == ["System", "Light", "Dark"]
