import argparse
import importlib.abc
import sys
from importlib.metadata import EntryPoint
from importlib.metadata import entry_points

from compas.plugins import ExtensionPoint
from compas.plugins import PluginManager

ENTRY_POINT_GROUP = "compas.plugins"
ENTRY_POINT_NAME = "compas_viewer"
ENTRY_POINT_VALUE = "compas_viewer.plugins"
FORBIDDEN_MODULES = {"OpenGL", "PySide6", "compas_viewer.scene", "compas_viewer.viewer"}
EXPECTED_EXTENSION_POINTS = {
    ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "clear"),
    ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "before_draw"),
    ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "after_draw"),
    ExtensionPoint("https://plugins.compas.dev/", "factories", "register_scene_operations"),
    ExtensionPoint("https://plugins.compas.dev/", "factories", "register_scene_attribute_contributions"),
}


class BlockGraphicsImports(importlib.abc.MetaPathFinder):
    """Fail if plugin discovery tries to import a graphics runtime."""

    def find_spec(self, fullname, path, target=None):
        if fullname.partition(".")[0] in {"OpenGL", "PySide6"}:
            raise ModuleNotFoundError(f"Plugin discovery imported optional graphics runtime {fullname!r}.")
        return None


def verify_plugin_discovery(matches: list[EntryPoint] | None = None) -> None:
    """Verify plugin discovery without graphics dependencies.

    Parameters
    ----------
    matches
        Explicit entry points for source-tree verification. By default, inspect
        the installed package metadata.

    """
    loaded_before = FORBIDDEN_MODULES.intersection(sys.modules)
    if loaded_before:
        raise RuntimeError(f"Graphics modules were loaded before plugin discovery: {sorted(loaded_before)}")

    matches = matches or [entry_point for entry_point in entry_points(group=ENTRY_POINT_GROUP) if entry_point.name == ENTRY_POINT_NAME]
    if len(matches) != 1 or matches[0].value != ENTRY_POINT_VALUE:
        raise RuntimeError("Expected one installed compas_viewer.plugins entry point.")

    sys.meta_path.insert(0, BlockGraphicsImports())
    manager = PluginManager(entry_points_provider=lambda *, group: matches if group == ENTRY_POINT_GROUP else [])
    if manager.load_plugins() != len(EXPECTED_EXTENSION_POINTS):
        raise RuntimeError("The installed viewer entry point registered an unexpected number of plugins.")
    if set(manager.registry) != EXPECTED_EXTENSION_POINTS:
        raise RuntimeError("The installed viewer entry point registered unexpected extension points.")

    loaded_after = FORBIDDEN_MODULES.intersection(sys.modules)
    if loaded_after:
        raise RuntimeError(f"Plugin discovery loaded graphics modules: {sorted(loaded_after)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-tree", action="store_true")
    arguments = parser.parse_args()
    source_matches = [EntryPoint(name=ENTRY_POINT_NAME, value=ENTRY_POINT_VALUE, group=ENTRY_POINT_GROUP)] if arguments.source_tree else None
    verify_plugin_discovery(source_matches)
