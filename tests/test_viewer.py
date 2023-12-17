from pathlib import Path

from compas import json_load

from compas_viewer import DATA
from compas_viewer import Viewer
from compas_viewer.configurations import ViewerConfig
from compas_viewer.configurations import ViewerConfigData


def test_default_config():
    viewer = Viewer()
    viewer_config = json_load(Path(DATA, "default_config", "viewer.json"))
    assert isinstance(viewer_config, ViewerConfig)
    assert viewer.about == viewer_config.about
    assert viewer.title == viewer_config.title
    assert viewer.width == viewer_config.width
    assert viewer.height == viewer_config.height
    assert viewer.full_screen == viewer_config.full_screen
    assert viewer.statusbar_text == viewer_config.statusbar_text
    assert viewer.show_fps == viewer_config.show_fps


def test_custom_config():
    config: ViewerConfigData = {
        "about": "This is a custom viewer",
        "title": "Custom Viewer",
        "width": 100,
        "height": 100,
        "full_screen": False,
        "statusbar_text": "Custom Status Bar",
        "show_fps": True,
    }
    viewer = Viewer(config=config)
    assert viewer.about == config["about"]
    assert viewer.title == config["title"]
    assert viewer.width == config["width"]
    assert viewer.height == config["height"]
    assert viewer.full_screen == config["full_screen"]
    assert viewer.statusbar_text == config["statusbar_text"]
    assert viewer.show_fps == config["show_fps"]

