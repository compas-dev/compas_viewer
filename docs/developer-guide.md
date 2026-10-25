# Developer Guide

This guide describes the architecture, extension points, and contribution workflow of COMPAS Viewer. For operating the viewer and its built-in tools, see the [user guide](user-guide.md).

## Set up a development environment

COMPAS Viewer supports Python 3.12 and newer:

```bash
git clone https://github.com/compas-dev/compas_viewer.git
cd compas_viewer
python -m pip install -e ".[dev,docs]"
```

The repository uses `invoke` for its standard workflows:

```bash
invoke test
invoke check
invoke docs
invoke format
```

Focused checks are useful while developing:

```bash
pytest -q tests/test_config.py
ruff check src tests
pyright src/compas_viewer
mkdocs build --strict
```

## Architecture

The main responsibilities are deliberately separated:

| Layer | Responsibility |
| --- | --- |
| `Viewer` | Application lifecycle and coordination |
| `ViewerScene` | Scene hierarchy and COMPAS scene-object creation |
| Scene objects | Adapt COMPAS data to renderable points, lines, and faces |
| `Renderer` | OpenGL resources, drawing, picking, camera, and overlays |
| Components | Qt presentation and interaction |
| Commands | User operations and input-binding metadata |
| Command registry | Stable runtime lookup for commands |
| UI definitions | Runtime menu and sidebar composition |
| Configuration | Serializable startup preferences and defaults |

`Viewer`, scene objects, and UI components use the shared viewer instance exposed by the project's singleton infrastructure. Avoid constructing hidden secondary viewers inside extensions.

## Configuration and runtime composition

Configuration contains persistent values only. `Config`, its nested dataclasses, and `Color` values can round-trip through dictionaries and JSON:

```python
from compas_viewer.config import Config

config = Config()
config.window.width = 1440
config.renderer.rendermode = "wireframe"
config.to_json("viewer.json")
```

The root configuration currently contains:

- `window`: window size, title, and related preferences.
- `ui`: appearance and component visibility.
- `display`: default scene-object colors and sizes.
- `renderer`: grid, render mode, background, and selection styling.
- `camera`: initial camera parameters and interaction increments.
- `unit` and `vectorsize`: viewer-wide geometric preferences.

`schema_version` protects persisted data. `Config.from_dict` migrates supported legacy fields and rejects files written by a newer unsupported schema.

Do not place callbacks, Qt widgets, commands, or plugin objects in configuration. Runtime composition belongs in the command registry and UI definitions.

## Commands and input bindings

A `Command` combines a callback with its visible title and optional keyboard, mouse, or wheel binding:

```python
from compas_viewer.commands import Command


def report_selection(viewer, verbose=False):
    selected = [obj for obj in viewer.scene.objects if obj.is_selected]
    print(f"{len(selected)} selected")
    if verbose:
        print([obj.name for obj in selected])


command = Command(
    title="Report Selection",
    callback=report_selection,
    keybinding="R + CTRL",
)
```

Register commands under stable, namespaced identifiers:

```python
viewer.register_command("example.report_selection", command)
```

Registration immediately activates the command's input bindings. Duplicate identifiers are rejected unless `replace=True` is explicit.

Add the registered command to a menu by identifier:

```python
viewer.add_menu_item(
    "Tools",
    {
        "title": "Report Selection",
        "command": "example.report_selection",
    },
)
```

Arguments remain part of the UI definition rather than the persistent config:

```python
viewer.add_menu_item(
    "Tools",
    {
        "title": "Report Verbosely",
        "command": "example.report_selection",
        "kwargs": {"verbose": True},
    },
)
```

Built-in identifiers use the `viewer.*` namespace. Third-party packages should use a package-specific prefix to avoid collisions.

Default menu and sidebar structures live in `compas_viewer.uidefinitions`. They refer to command IDs rather than importing callbacks, keeping UI composition separate from serialization.

## COMPAS plugin discovery

The package exposes its COMPAS plugin module through a project entry point:

```toml
[project.entry-points."compas.plugins"]
compas_viewer = "compas_viewer.plugins"
```

`compas_viewer.plugins` registers Viewer scene-object adapters in the `factories` plugin category. `Viewer` also calls `ensure_scene_objects_registered()` during startup. This covers source checkouts and processes in which another package populated the global COMPAS scene registry before the viewer plugin was requested.

An external distribution should expose its own plugin module through the same entry-point group rather than relying on import side effects.

## Add support for a data or geometry type

A scene-object adapter translates an underlying object into shader data. For a geometry that is naturally represented by points and lines, derive from `GeometryObject` and implement the relevant typed properties or `_read_*_data` methods.

```python
from compas.geometry import Point
from compas_viewer.scene import GeometryObject


class LandmarkObject(GeometryObject):
    @property
    def points(self):
        landmark = self.geometry
        return [Point(landmark.x, landmark.y, landmark.z)]
```

Register it for the Viewer context from a COMPAS plugin:

```python
from compas.plugins import plugin


@plugin(category="factories")
def register_scene_objects():
    from compas.scene import register

    register(Landmark, LandmarkObject, context="Viewer")
```

Use the narrowest useful base class:

- `ViewerSceneObject` for non-geometric scene behavior.
- `GeometryObject` for COMPAS geometry rendered as points, lines, or faces.
- `ShapeObject` for tessellated COMPAS shapes with `u` and `v` resolution.
- `MeshObject` or `GraphObject` when adapting corresponding data structures.
- `BufferObject` for already prepared rendering buffers.

Every scene object exposes its underlying object through `data`, constructor-derived values through `parameters`, and detailed inspection through `parameter_info`.

## Render-data lifecycle

`ViewerSceneObject.init()` creates render data, bounds, and the instance color used for picking. The four render-data channels are:

- `_points_data`
- `_lines_data`
- `_frontfaces_data`
- `_backfaces_data`

Each populated channel contains positions, colors, and element indices.

Use the appropriate update path:

- `sceneobject.update(update_transform=True)` for transformation-only changes.
- `sceneobject.update(update_data=True)` for position changes that preserve topology.
- `sceneobject.refresh_data()` followed by `renderer.rebuild_buffers()` when parameter changes may alter vertex or element counts.

The buffer manager combines scene-object data into shared OpenGL buffers. Do not make scene objects own global OpenGL lifecycle decisions unless a specialized overlay requires it.

## Selection and picking

The renderer assigns a unique instance color to each selectable scene object. Picking renders or reads those colors rather than relying on geometric ray intersections. Consequently:

- Every selectable object must contribute a valid instance color.
- Point and line widths affect their visible picking footprint.
- Directional window selection compares colors within the rectangle with colors in the complete instance map to distinguish fully contained objects from intersections.

After changing scene hierarchy or topology, rebuild buffers so object indices, transforms, settings, and picking colors remain synchronized.

## UI components

Components wrap Qt widgets and share access to the active viewer through `Base`. Common bound controls include:

- `BooleanToggle`
- `ChoiceEdit`
- `ColorPicker`
- `NumberEdit`
- `TextEdit`

`Container(..., compact=True)` applies the shared compact sidebar policy: content margins, row margins, spacing, size policy, and maximum row height. Use this for inspector-style forms instead of repeating layout constants.

The scene-object parameter dialog intentionally edits only writable scalar constructor parameters. Extend `ParameterForm` with explicit editors and conversion rules for structured values such as `Point`, `Vector`, `Frame`, and `Color`; do not parse arbitrary executable input.

## Configuration changes and runtime state

`viewer.state` is the single observable source for viewer-wide UI state. Its
dotted paths refer to values in the persistent configuration backing store:

```python
viewer.state.set("renderer.show_grid", False)
viewer.state.set("renderer.rendermode", "wireframe")
viewer.state.toggle("ui.sidebar.show")
```

State changes update the configuration and publish a Qt signal. Menus, display
controls, component visibility, the viewport, and the renderer subscribe to
the paths they own and update immediately. Use `viewer.state` for runtime
changes instead of assigning directly to `viewer.config`; direct configuration
assignment is intended for setup before constructing the viewer.

Bound controls that assign a configuration attribute before their callback can
call `viewer.state.notify(path)` to publish the resulting value.

For coupled settings, prefer a method on the owning runtime object. `Viewer.set_appearance`, viewport unit changes, renderer view changes, and grid rebuilding are examples of boundaries where a plain dataclass assignment is insufficient.

## Images and animation

`Viewer.save_image` and `Viewer.record_animation` can create output without entering the visible interactive event loop. Internally, Qt still needs an exposed native surface for `QOpenGLWidget`; the viewer temporarily creates an off-screen surface and restores the widget state afterward.

When adding output features:

- Restore widget sizes and visibility in `finally` blocks.
- Process Qt events before reading the framebuffer.
- Keep deterministic frame updates separate from encoding.
- Validate dimensions, frame rate, output suffix, and loop count before allocating frames.

## Tests

Test public behavior at the narrowest layer that owns it:

- Configuration serialization and migration in config tests.
- Registry resolution and duplicate handling without constructing a GUI.
- Qt components using `QT_QPA_PLATFORM=offscreen` when practical.
- Scene-object render data without a live OpenGL context where possible.
- Renderer and lifecycle behavior through focused integration tests.

Always finish a change with:

```bash
ruff check src tests
pyright src/compas_viewer
pytest -q
git diff --check
```

Build documentation changes strictly:

```bash
mkdocs build --strict
```

See [Building the Documentation](building-docs.md) for local preview,
navigation, snippets, assets, API pages, CI, and troubleshooting.

## Documentation conventions

Public Python APIs use MkDocs-compatible NumPy-style docstrings. Types belong in annotations and return types, not repeated in parameter descriptions. Except for one-line docstrings, leave a blank line before the closing quotes.

Examples in Markdown should be executable or clearly focused fragments. Reuse repository files with the snippets extension when an example has a corresponding `.py` source:

```text
--8<-- "docs/examples/scene/groups.py"
```

Keep tutorials task-oriented, examples focused on one capability, and the API reference generated from source docstrings.
