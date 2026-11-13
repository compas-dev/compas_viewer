from types import SimpleNamespace

import pytest

from compas.colors import Color
from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.datastructures import VolMesh
from compas.geometry import Sphere
from compas_viewer import Viewer
from compas_viewer.config import Config
from compas_viewer.plugins import ensure_scene_objects_registered
from compas_viewer.scene import ViewerScene


PALETTES = {
    "light": {
        "viewport": Color.from_hex("#FAFAFA"),
        "surface": Color.from_hex("#D8DEE4"),
        "line": Color.from_hex("#4B5563"),
        "point": Color.from_hex("#111827"),
    },
    "dark": {
        "viewport": Color.from_hex("#10161B"),
        "surface": Color.from_hex("#3A4650"),
        "line": Color.from_hex("#B8C2CC"),
        "point": Color.from_hex("#F2F6F8"),
    },
}


def _viewer(scheme: str) -> Viewer:
    viewer = object.__new__(Viewer)
    viewer._config = Config()
    viewer._effective_appearance = lambda appearance=None: scheme
    return viewer


def _scene(scheme: str) -> ViewerScene:
    ensure_scene_objects_registered()
    scene = ViewerScene()
    colors = PALETTES[scheme]
    scene.attach(SimpleNamespace(running=False, _content_color=lambda role: colors[role]))
    return scene


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_automatic_and_explicit_viewport_backgrounds(scheme):
    viewer = _viewer(scheme)

    assert viewer.backgroundcolor == PALETTES[scheme]["viewport"]

    explicit = Color(0.1, 0.2, 0.3)
    viewer.config.renderer.backgroundcolor = explicit

    assert viewer.backgroundcolor is explicit


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_geometry_defaults_use_scheme_channels_at_creation(scheme):
    scene = _scene(scheme)
    sceneobject = scene.add(Sphere(1.0))

    assert sceneobject.pointcolor == PALETTES[scheme]["point"]
    assert sceneobject.linecolor == PALETTES[scheme]["line"]
    assert sceneobject.surfacecolor == PALETTES[scheme]["surface"]


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_mesh_graph_and_volmesh_defaults_use_scheme_channels(scheme):
    scene = _scene(scheme)
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])
    graph = Graph()
    graph.add_node(0, x=0, y=0, z=0)
    graph.add_node(1, x=1, y=0, z=0)
    graph.add_edge(0, 1)
    volmesh = VolMesh.from_vertices_and_cells(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
        [[(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]],
    )

    meshobject = scene.add(mesh)
    graphobject = scene.add(graph)
    volmeshobject = scene.add(volmesh)

    assert meshobject.vertexcolor.default == PALETTES[scheme]["point"]
    assert meshobject.edgecolor.default == PALETTES[scheme]["line"]
    assert meshobject.facecolor.default == PALETTES[scheme]["surface"]
    assert graphobject.nodecolor.default == PALETTES[scheme]["point"]
    assert graphobject.edgecolor.default == PALETTES[scheme]["line"]
    assert volmeshobject.vertexcolor.default == PALETTES[scheme]["point"]
    assert volmeshobject.edgecolor.default == PALETTES[scheme]["line"]
    assert volmeshobject.facecolor.default == PALETTES[scheme]["surface"]
    assert volmeshobject.cellcolor.default == PALETTES[scheme]["surface"]


def test_explicit_base_preserves_core_channel_derivation_and_explicit_channels_win():
    scene = _scene("dark")
    base = Color(0.2, 0.3, 0.4)
    point = Color(0.9, 0.1, 0.2)
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])

    derived = scene.add(mesh, color=base)
    overridden = scene.add(mesh.copy(), color=base, vertexcolor=point)

    assert derived.facecolor.default == base
    assert derived.vertexcolor.default == derived.contrastcolor
    assert derived.edgecolor.default == derived.contrastcolor
    assert overridden.vertexcolor.default == point
    assert overridden.facecolor.default == base


def test_scheme_switch_changes_automatic_viewport_but_not_existing_geometry():
    active = ["light"]
    viewer = object.__new__(Viewer)
    viewer._config = Config()
    viewer._effective_appearance = lambda appearance=None: active[0]
    viewer.running = False
    ensure_scene_objects_registered()
    scene = ViewerScene()
    scene.attach(viewer)
    sceneobject = scene.add(Sphere(1.0))

    assert viewer.backgroundcolor == PALETTES["light"]["viewport"]
    assert sceneobject.surfacecolor == PALETTES["light"]["surface"]

    active[0] = "dark"

    assert viewer.backgroundcolor == PALETTES["dark"]["viewport"]
    assert sceneobject.surfacecolor == PALETTES["light"]["surface"]


def test_partial_headless_viewer_uses_deterministic_light_defaults(monkeypatch):
    viewer = object.__new__(Viewer)
    viewer._config = Config()
    viewer.running = False
    scene = ViewerScene()
    scene.attach(viewer)
    monkeypatch.setattr("compas_viewer.viewer.QApplication", SimpleNamespace(instance=lambda: None))

    sceneobject = scene.add(Sphere(1.0))

    assert viewer.backgroundcolor == PALETTES["light"]["viewport"]
    assert sceneobject.pointcolor == PALETTES["light"]["point"]
    assert sceneobject.linecolor == PALETTES["light"]["line"]
    assert sceneobject.surfacecolor == PALETTES["light"]["surface"]
