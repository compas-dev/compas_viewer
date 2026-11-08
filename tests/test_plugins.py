from importlib.metadata import EntryPoint
import os
from pathlib import Path
import subprocess
import sys

from compas.plugins import ExtensionPoint
from compas.plugins import PluginManager


ROOT = Path(__file__).parents[1]


def test_entry_point_exposes_current_extension_points():
    entry_point = EntryPoint(name="compas_viewer", value="compas_viewer.plugins", group="compas.plugins")
    manager = PluginManager(entry_points_provider=lambda *, group: [entry_point])

    assert manager.load_plugins() == 5
    assert set(manager.registry) == {
        ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "clear"),
        ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "before_draw"),
        ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "after_draw"),
        ExtensionPoint("https://plugins.compas.dev/", "factories", "register_scene_operations"),
        ExtensionPoint("https://plugins.compas.dev/", "factories", "register_scene_attribute_contributions"),
    }


def test_source_entry_point_discovery_is_graphics_free(tmp_path):
    environment = os.environ.copy()
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, [source_path, environment.get("PYTHONPATH")]))
    result = subprocess.run(
        [sys.executable, str(ROOT / ".github" / "verify_plugin_discovery.py"), "--source-tree"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_scene_plugin_registers_viewer_operations_without_replacing_types():
    from compas.scene import SceneObject
    from compas.scene.context import SCENE_OPERATIONS
    import compas_viewer.plugins as viewer_plugins

    SCENE_OPERATIONS.pop("Viewer", None)
    viewer_plugins.register_scene_operations()

    assert set(SCENE_OPERATIONS["Viewer"][SceneObject]) == {"draw", "clear"}


def test_scene_attribute_plugin_is_lightweight():
    import compas_viewer.plugins as viewer_plugins

    assert viewer_plugins.register_scene_attribute_contributions() is None


def test_registration_is_triggered_when_other_contexts_already_exist():
    from compas.scene.context import SCENE_OPERATIONS
    import compas_viewer.plugins as viewer_plugins

    SCENE_OPERATIONS.pop("Viewer", None)
    SCENE_OPERATIONS["Other"] = {}
    viewer_plugins.ensure_scene_objects_registered()

    assert "Viewer" in SCENE_OPERATIONS
