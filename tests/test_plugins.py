from importlib.metadata import EntryPoint

from compas.geometry import Brep
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import PolygonalSurface
from compas.geometry import Surface
from compas.plugins import ExtensionPoint
from compas.plugins import PluginManager
from compas.scene.context import ITEM_SCENEOBJECT

import compas_viewer.plugins as viewer_plugins
import compas_viewer.scene as viewer_scene


def test_entry_point_exposes_current_extension_points():
    entry_point = EntryPoint(name="compas_viewer", value="compas_viewer.plugins", group="compas.plugins")
    manager = PluginManager(entry_points_provider=lambda *, group: [entry_point])

    assert manager.load_plugins() == 4
    assert set(manager.registry) == {
        ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "clear"),
        ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "before_draw"),
        ExtensionPoint("https://plugins.compas.dev/", "drawing-utils", "after_draw"),
        ExtensionPoint("https://plugins.compas.dev/", "factories", "register_scene_objects"),
    }


def test_scene_plugin_registers_stable_core_geometry_types():
    had_context = "Viewer" in ITEM_SCENEOBJECT
    registry = ITEM_SCENEOBJECT["Viewer"]
    previous = dict(registry)

    try:
        registry.clear()
        viewer_plugins.register_scene_objects()

        assert registry[Brep] is viewer_scene.BRepObject
        assert registry[NurbsCurve] is viewer_scene.NurbsCurveObject
        assert registry[NurbsSurface] is viewer_scene.SurfaceObject
        assert registry[Surface] is viewer_scene.SurfaceObject
        assert registry[PolygonalSurface] is viewer_scene.PolygonalSurfaceObject
    finally:
        if had_context:
            registry.clear()
            registry.update(previous)
        else:
            del ITEM_SCENEOBJECT["Viewer"]


def test_registration_is_triggered_when_other_contexts_already_exist():
    registry = ITEM_SCENEOBJECT["Viewer"]
    previous = dict(registry)
    ITEM_SCENEOBJECT[None][Surface] = viewer_scene.GeometryObject

    try:
        registry.clear()
        viewer_plugins.ensure_scene_objects_registered()

        assert registry[Surface] is viewer_scene.SurfaceObject
        assert registry[PolygonalSurface] is viewer_scene.PolygonalSurfaceObject
    finally:
        registry.clear()
        registry.update(previous)
