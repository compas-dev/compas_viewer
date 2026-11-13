# Developer Guide

This guide describes the architecture, extension points, and contribution workflow of COMPAS Viewer. For operating the viewer and its built-in tools, see the [user guide](user-guide.md).

## Set up a development environment

COMPAS Viewer supports Python 3.12 and newer:

```bash
git clone https://github.com/compas-dev/compas_viewer.git
cd compas_viewer
uv sync --frozen --group dev --group docs
```

The direct uv commands are authoritative:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
QT_QPA_PLATFORM=offscreen uv run pytest
QT_QPA_PLATFORM=offscreen uv run mkdocs build --strict
```

Thin Invoke aliases remain available as `uv run invoke check`, `uv run invoke
test`, and `uv run invoke docs`. Focused checks are useful while developing:

```bash
QT_QPA_PLATFORM=offscreen uv run pytest -q tests/test_config.py
uv run ruff check src tests
uv run pyright
```

## Architecture

The main responsibilities are deliberately separated:

| Layer | Responsibility |
| --- | --- |
| `Viewer` | Application lifecycle and coordination |
| `ViewerScene` | Spatial hierarchy plus the separate ordered annotation collection |
| Scene objects | Adapt COMPAS data to renderable points, lines, and faces |
| Annotation render objects | Render non-spatial text, arrows, and dimensions outside shared geometry buffers |
| `Renderer` | OpenGL resources, drawing, picking, camera, and overlays |
| Components | Qt presentation and interaction |
| Commands | User operations and input-binding metadata |
| Command registry | Stable runtime lookup for commands |
| UI definitions | Runtime menu and sidebar composition |
| Configuration | Serializable startup preferences and defaults |
| Viewer state | Observable spatial selection, annotation selection, and runtime state |
| Transform history | Reversible Viewer transform transactions |

`Viewer`, scene objects, and UI components use the shared viewer instance exposed by the project's singleton infrastructure. Avoid constructing hidden secondary viewers inside extensions.

## Configuration and runtime composition

Configuration contains persistent values only. `Config`, its nested dataclasses, and `Color` values can round-trip through dictionaries and JSON:

```python
from compas_viewer.config import Config

config = Config()
config.window.title = "Analysis Viewer"
config.window.width = 1440
config.renderer.rendermode = "wireframe"
config.measurement.unit = "mm"
config.measurement.precision = 3
config.to_json("viewer.json")
```

`window.title`, `window.icon`, and `window.fullscreen` are startup settings.
The title is shared by the Qt application and main window. An icon value of
`None` selects the packaged COMPAS icon; a custom icon must be an existing
absolute filesystem path. Viewer validates and applies this identity before it
constructs the Qt application. Changing these values afterward has no promised
live effect.

The root configuration currently contains:

- `window`: window size, title, icon, and fullscreen startup mode.
- `ui`: appearance and component visibility.
- `renderer`: grid, render mode, background, and selection styling.
- `camera`: initial camera parameters and interaction increments.
- `measurement`: coordinate-unit declaration and decimal display precision.
- `vectorsize`: the viewer-wide vector-arrow preference.

`ui.appearance` retains the closed `system`, `light`, and `dark` values. These
select the effective light or dark variant of one built-in COMPAS Viewer theme;
they are not a general theme-extension interface. A private semantic token
module constructs the application-wide Qt palette and the narrow stylesheet
used for focus, interaction, links, and System-section hierarchy. Viewer keeps
the platform UI font, packaged or configured application icon, and existing
monochrome UI icons. Button icons are tinted privately from the active Qt
button-text palette and retint when the application palette changes; this does
not affect the packaged or configured application icon.

Theme ownership includes Qt application chrome and a narrow Viewer content
palette. `renderer.backgroundcolor=None` is the sole automatic marker; the
effective light or dark scheme resolves it to `#FAFAFA` or `#10161B` at draw
time. An explicit renderer background is never replaced. New Viewer scene
objects resolve omitted channels at creation to surface `#D8DEE4`/`#3A4650`,
line `#4B5563`/`#B8C2CC`, and point `#111827`/`#F2F6F8` for light/dark. The
resolved values remain concrete and do not change on a later appearance
switch. Explicit, deserialized, and existing content remains authoritative;
grid, selection, legends, and overlays retain their own ownership. This is a
Viewer-specific palette, not an organization-wide COMPAS brand standard, and
Core keeps its existing white defaults.

Viewer applies creation defaults to supported Geometry, Mesh, Graph, and
VolMesh objects only when both the base color and the relevant specialized
channel are omitted. An explicit point/vertex, line/edge, or surface/face
channel always wins. When the base `color` is explicit and a specialized
channel is omitted, the existing Core derivation from that base color remains
authoritative. Collections and buffer-backed objects keep their established
explicit and per-element color semantics; Viewer does not invent unsupported
semantic roles for them.

`schema_version` protects persisted data. Schema version 4 is closed: unknown
and retired fields are rejected. `Config.from_dict` migrates versions 0
through 3. Versions 0--2 retain supported values and add the default
`measurement` group. Schema 3 always becomes an explicit background: a stored
color remains unchanged, while an omitted field receives the former
`#D8DDE2` default. Migration never guesses that an old concrete value was
automatic.
Versions 0 and 1 also drop only these known retired fields:

- Root `commands`, `display`, and `unit` fields.
- `window.about` and `renderer.opacity`.
- `ui.display`, `ui.view3d`, and per-component `items` fields.
- `ui.sidebar.show_widgets` and `ui.sidebar.sceneform`.

Each nested configuration group validates its own values and reports complete
paths such as `renderer.gridmode`.

At runtime, the **Grid and Units** section of the **System** sidebar tab
updates these settings through `ViewerState.set_measurement_unit` and
`ViewerState.set_measurement_precision`. It also owns the existing grid state
paths. Unit and precision affect labels only: they do not convert coordinates,
grid spacing, configure snapping, or define geometry tolerance. Process-wide
`compas.tolerance.TOL` remains a computational service and is not exposed as a
Viewer setting. Camera, Display, and Grid and Units use one private aligned
two-column layout; this is not a generic component-extension API.

Measurement precision has one shared Core and Viewer domain: integer values
from 0 through 15 inclusive. Configuration validation and both precision
editors reject values outside that domain; Core assignment and configuration
validation raise `ValueError`, and no path clamps or truncates. Existing
configuration above 15 is rejected without migration or a
configuration-schema change.

The default toolbar contains command-backed Zoom Selected, Zoom Extents, and
Capture View buttons followed by one `menu_button` for Measurement. Its fixed
items reuse `viewer.inspect_distance`, `viewer.add_fixed_distance_dimension`,
`viewer.add_associative_distance_dimension`, and
`viewer.cancel_measurement`. The toolbar is visible unless
`ui.toolbar.show` is explicitly false. Existing custom text-only,
text-plus-icon, unbound, and state-bound buttons remain supported;
`viewer.toolbar_items` remains the runtime composition boundary. The narrow
menu-button definition contains command items only and does not establish a
general toolbar-widget registry.

Perspective, Top, Front, Right, and Ortho and the four render modes live in one
private grouped `QToolButton`/`QMenu` over the top-right of the viewport. The
two titled, exclusive groups observe `renderer.view` and
`renderer.rendermode`, reuse the existing commands, and synchronize with the
application View menu, Display form, and public state. Menu closure restores
renderer focus. The control is private Viewer chrome: it does not enter the
public mouse-transparent overlay layer and does not establish a general
viewport-widget registry.

Applications may subclass `Config` and add typed nested `ConfigBase`
dataclasses. Declared fields round-trip through dictionaries and JSON; dynamic
attributes do not. Validate custom groups explicitly, following the built-in
group pattern.

Do not place callbacks, Qt widgets, commands, or plugin objects in configuration. Runtime composition belongs in the command registry and UI definitions.

## Commands and input bindings

A `Command` combines a callback with its visible title and optional keyboard, mouse, or wheel binding:

```python
from compas_viewer.commands import Command


def report_selection(viewer, verbose=False):
    selected = viewer.state.selection.objects
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

## Work with selection from code

`viewer.state.selection` is the single object-selection model shared by the
viewport, scene tree, commands, renderer, and programmatic integrations. It
stores stable scene-object GUIDs and resolves them against the current Viewer
scene in selection order:

```python
first = viewer.scene.add(first_geometry, name="First")
second = viewer.scene.add(second_geometry, name="Second")
third = viewer.scene.add(third_geometry, name="Third")

viewer.state.selection.replace((first, second))
viewer.state.selection.add(third)
viewer.state.selection.remove(first)
viewer.state.selection.toggle(second)

for sceneobject in viewer.state.selection:
    print(sceneobject.name)

viewer.state.selection.clear()
```

Each effective mutation publishes one complete selection change. Duplicate
objects and operations that leave the selection unchanged publish nothing.
Use `selection.objects` for ordered scene objects and `selection.guids` for
their ordered stable identifiers. Selection is transient Viewer state: it is
not stored on scene objects and does not participate in scene or configuration
serialization.

Annotations use a separate runtime selection and never enter spatial transform
commands:

```python
from compas.colors import Color
from compas.scene import TextAnnotation

entry = viewer.scene.add_annotation(
    TextAnnotation("Result", (0, 0, 0)),
    name="Result label",
    label_background=Color(0.0, 0.0, 0.0, 0.75),
    label_background_padding=3.0,
)
viewer.state.annotation_selection.replace((entry,))
viewer.refresh_annotations((entry,))
```

`SceneAnnotation.label_background` and
`SceneAnnotation.label_background_padding` are durable presentation. They
apply to text and distance labels; padding is nonnegative and measured in
logical pixels. Arrow entries accept only the transparent default because they
have no label. A background change uses the annotation-only refresh path and
does not alter semantic text, anchors, units, values, or precision.

Interactive Viewer completion of a new persistent distance dimension resolves
an enabled background from the effective scheme: `#FAFAFAE6` for light or
`#10161BE6` for dark, with two logical pixels of padding. This is a narrow
acquisition default. Core construction, programmatic `add_annotation`, existing
serialized dimensions, and explicit values retain their previous behavior.
The resolved background is concrete and does not change after a later scheme
switch.

`viewer.scene.annotations` preserves durable collection order independently of
the scene hierarchy. `viewer.state.annotation_selection` is transient and
unserialized. The **Annotations** tab owns annotation naming, visibility,
removal, distance-style editing, and optional label-background controls for
text-bearing annotations; the **Scene** tab and spatial selection remain
unchanged. The Label Background group maps a disabled checkbox to
`label_background=None`, edits alpha-aware color and nonnegative logical-pixel
padding when enabled, blocks editor signals during synchronization, and
refreshes only the affected annotation. Arrow, unresolved-data, no-selection,
and multiple-selection states hide the group.

For exactly one selected entry bound to a `DistanceDimension`, Annotations also
owns a separate **Measurement Format** group. It trims Coordinate Unit input,
maps blank input to `None`, and assigns Display Precision through Core's
validated 0–15 property. A changed value refreshes only that annotation with
`viewer.refresh_annotations((entry,))`; synchronization blocks editor signals,
and Escape in the unit editor restores the durable value without invoking
global deselection. No selection, multiple selection, non-distance items, and
unresolved data bindings hide the group. An associative dimension with
geometrically unresolved anchors remains editable when its semantic data item
is still bound.

These durable per-dimension values do not update
`viewer.config.measurement`. **Grid and Units** continues to supply transient
formatting and snapshots for dimensions created afterward. No unit conversion,
bulk editing, spatial-buffer rebuild, or generic property-editor path is
involved. An explicit semantic label remains a verbatim override of generated
value, precision, and unit text, but it does not bypass format validation.

The same single-dimension details surface owns **Spatial Layout**. It replaces
the complete immutable-value-style `DistanceDimensionLayout` atomically from a
finite signed offset and either three finite world-normal components or three
blank fields. Field traversal retains partial drafts; **Apply Layout** is the
only commit boundary. Partial normals, non-finite values, and invalid
application restore the durable layout without refresh. Successful application
calls `viewer.refresh_annotations((entry,))` once and never rebuild spatial
buffers.
The derived status follows the accepted order: zero displacement, unresolved
anchor, coincident anchors, missing normal, zero normal, parallel normal, then
resolved. Rendering includes measured anchors and displaced endpoints in
annotation bounds, keeps the measured value tied to the original anchors, and
uses no camera-dependent fallback.

Spatial and annotation selections may coexist. Sidebar tab changes preserve
both, object picking changes only spatial selection, and annotation-list
interaction changes only annotation selection. Outside an active measurement,
an unmodified empty viewport click clears both selections and Ctrl-clicking
empty background changes neither. Escape cancels an active measurement first
and otherwise clears both selections.

Delete remains focus-owned. Annotation-list and annotation-detail focus remove
selected annotations, while Scene-tree and renderer focus remove selected
scene objects. Menu invocation follows the active Scene or Annotations tab and
is disabled in System. Text and numeric editors retain local Delete behavior.
Neither operation crosses the collection boundary when both selections exist.

Default menu and sidebar structures live in `compas_viewer.uidefinitions`.
They refer to command IDs rather than importing callbacks, keeping UI
composition separate from serialization. The fixed geometry hierarchy belongs
to **Scene → Add**; Measure continues to own interactive acquisition. The
built-in right sidebar has four
stable domains: **Scene** for the spatial hierarchy and object details,
**Data** for the flat referenced-item projection, **Annotations** for the
ordered annotation list and annotation details, and **System** for Camera,
Display, and Grid and Units. Dynamic detail
updates do not resize or rebuild unrelated domains.

Data is a read-only Viewer projection, not a store. It walks spatial objects
in hierarchy order followed by annotations in collection order, deduplicates
their item GUIDs, and resolves bound instances only through
`scene.item_store`. Unresolved GUIDs remain rows and no resolver is invoked.
Its local selection is not part of `ViewerState`. The modal Data Details
dialog reads generic public constructor attributes without traversing
`__data__`; Mesh and Graph reuse lazy declared-domain tables with editing
disabled. Refreshing this projection does not rebuild renderer buffers.
Scene owns a noncollapsible vertical splitter between its hierarchy and
editable details. Annotations owns a separate noncollapsible splitter between
its list and a vertically scrollable dimension-details area. Detail controls
retain their natural size and spacing when the splitter is reduced, and the two
splitter sizes remain independent. The Scene details
area replaces the old inline information textbox with a fixed **Details**
button. That button opens a main-window-owned, read-only modal snapshot for one
or multiple selected objects; it is disabled for no selection. Editable
attributes remain in the sidebar.
The Viewer derives resolution controls from the normalized Core editable-field
mapping and filters them by the represented producer. It does not define a
second resolution field or alias: cones and cylinders expose U; spheres, tori,
and capsules expose U and V; surfaces expose both; boxes and unknown shapes
expose neither. Core callbacks validate integer minima and the capsule's even V
constraint transactionally. A valid edit regenerates only the affected render
helper's representation and bounds before topology buffers and the Scene tree
are refreshed; the active editor is retained until its Qt signal callback has
returned. U/V spin boxes commit typed text once rather than rebuilding for each
keystroke. An invalid edit rolls back without a render or UI refresh. The
analytic geometry remains unchanged, while the scene-owned U/V values survive
scene serialization.
Shape and surface controls present their existing `show_lines`, `linecolor`,
and `linewidth` fields as wireframe settings; the durable field names are not
changed. Visibility flags, opacity, point or vertex size, and line or edge
width update only the affected settings-texture record with a current OpenGL
context and request one redraw. They do not refresh object data, tessellate a
parametric producer, or rebuild combined buffers. Color controls continue to
use the appearance-data refresh path.
The enclosing viewport splitter keeps the right sidebar non-collapsible, so
its configured minimum width remains authoritative.

`GridUnitSetting` is the only built-in component for grid, unit, and precision
controls. The retired `MeasurementSetting` item type and `"Units and
Measurement"` section identifier have no compatibility alias.

## Transient overlays and scalar inspections

Viewer-owned screen overlays remain outside Scene, picking, and serialization.
`ScreenTextOverlay` stores text, a normalized viewport position, horizontal and
vertical alignment, color, and optional label background with nonnegative
logical-pixel padding. `(0, 0)` is the top-left corner and `(1, 1)` is the
bottom-right. The background alpha controls opacity and `None` remains
transparent. Add and remove instances through `viewer.add_overlay` and
`viewer.remove_overlay`; the initial contract has no interactive placement,
management UI, or persistence.

`viewer.inspect_selected_area()` and `viewer.inspect_selected_volume()` are
UI-independent scalar operations. They require exactly one spatially selected
scene object and use its represented item's public `area` or `volume` method or
property. The methods return a finite nonnegative world-coordinate scalar.
Command callbacks alone format the current declared `unit²` or `unit³`, apply
display precision, and show result or error dialogs.

Scalar inspection uses the complete inherited world transformation. Area is
scaled exactly only for rigid, reflected, or uniformly scaled transformations;
non-uniform scale, shear, and projective transformations are rejected. Volume
uses the absolute determinant of an affine transformation's linear part and
rejects projective transformations. Missing APIs, unresolved items,
`NotImplementedError`, and `None` results are unsupported. Other backend
exceptions remain operation failures. Render tessellations are never an
implicit measurement fallback.

Both operations clear active or retained distance inspection before
validation, but retain no scalar-measurement state and do not modify Scene,
either selection, annotations, serialization, or transform history.

## COMPAS plugin discovery

The package exposes its COMPAS plugin module through a project entry point:

```toml
[project.entry-points."compas.plugins"]
compas_viewer = "compas_viewer.plugins"
```

`compas_viewer.plugins` registers Viewer `draw` and `clear` operations for
spatial scene objects and `SceneAnnotation` entries in the `factories` plugin
category. Plugin discovery imports neither Qt nor OpenGL.
`Viewer` also ensures these operations are registered during startup for source
checkouts without installed entry-point metadata.

An external distribution should expose its own plugin module through the same entry-point group rather than relying on import side effects.

## Add support for a data or geometry type

Register `draw` and `clear` operations for the stable semantic scene-object type
from a lightweight COMPAS plugin. Keep imports of the render implementation
inside the operation functions. Operation functions receive the owning scene,
the stable scene object, and the explicit application runtime. `draw` returns
opaque runtime handles; `clear` receives those handles for deterministic
cleanup.

```python
from compas.plugins import plugin


@plugin(category="factories")
def register_scene_operations():
    from compas.scene import GeometryObject
    from compas.scene import register_scene_operation
    from landmark_viewer.operations import clear_landmark
    from landmark_viewer.operations import draw_landmark

    register_scene_operation("Viewer", GeometryObject, "draw", draw_landmark)
    register_scene_operation("Viewer", GeometryObject, "clear", clear_landmark)
```

Every stable scene object exposes its referenced object through `item`. Viewer
runtime implementation classes are private and are not extension points.

## Contribute contextual object settings

Viewer builds its object inspector from the stable scene object's
`editable_attributes()` inventory. A package can filter that inventory or
replace an attribute's data-side update callback for one visualization
context. Contributions contain no widgets, labels, form metadata, represented
item parameters, or rendering callbacks.

Register contributions from a lightweight COMPAS plugin:

```python
from compas.plugins import plugin


@plugin(category="factories")
def register_scene_attribute_contributions():
    from compas.scene import ShapeObject
    from compas_viewer.forms import REMOVE_EDITABLE_ATTRIBUTE
    from compas_viewer.forms import register_scene_attribute_contribution

    register_scene_attribute_contribution(
        context="Viewer",
        sceneobject_type=ShapeObject,
        contribution="example.shape",
        attributes={
            "u": None,
            "opacity": REMOVE_EDITABLE_ATTRIBUTE,
        },
    )
```

`None` selects ordinary scene-object assignment. The explicit removal marker
hides an inherited editable attribute. Viewer infers Boolean, number, text,
and color controls from current values, omits unsupported values, and owns the
render-data rebuild, redraw, and inspector refresh after successful mutation.
Represented-item parameters remain on the separate parameter form path.

## Render-data lifecycle

The Viewer internally creates render data, bounds, and the instance color used
for picking. Its four internal render-data channels are:

- `_points_data`
- `_lines_data`
- `_frontfaces_data`
- `_backfaces_data`

Each populated channel contains positions, colors, and element indices.

The buffer manager combines these values into shared OpenGL buffers. Backend
operations and runtime state own GPU lifecycle decisions; stable scene objects
remain graphics-free.

Public integrations synchronize changes through four categorized Viewer
operations:

- `refresh_geometry(objects=None)` regenerates render data and rebuilds
  combined geometry buffers. Use it after represented coordinates or topology
  change.
- `refresh_appearance(objects=None)` updates appearance data and display
  settings without a full geometry rebuild.
- `refresh_transform(objects=None)` updates local transform buffers and cached
  world bounds for the requested objects and their descendants without
  rebuilding geometry.
- `refresh_hierarchy()` reconstructs transient render helpers, parent indices,
  picking state, selection membership, and buffers after hierarchy changes.
- `refresh_annotations(entries=None)` refreshes only annotation graphics and
  repaints the annotation layer; it never rebuilds shared spatial buffers.

`None` means all current targets for the corresponding object- or
annotation-scoped operation. Direct
external transformation mutation followed by `refresh_transform` invalidates
transform history because the Viewer cannot construct a reversible transaction
for the earlier value. Hierarchy refresh also invalidates transform history;
geometry and appearance refresh do not.

Use `Viewer.transform_objects` when a transformation should be atomic,
immediately synchronized, and reversible. It materializes and validates every
target before mutation, removes duplicate targets without changing their input
order, and accepts only objects from the current scene. For each object, one
world-space delta $\Delta$ is applied to its captured world transformation
$W_i$:

$$
W_i' = \Delta W_i
$$

The new local transformation is derived through the inverse captured parent
world transformation. A request containing both an ancestor and its descendant
is rejected because their simultaneous group semantics are intentionally
undefined. `Viewer.undo` and `Viewer.redo` operate only on these explicit
transform transactions; arbitrary command callbacks and domain mutations do
not enter Viewer history.

## Selection and picking

The renderer assigns a unique instance color to each selectable scene object. Picking renders or reads those colors rather than relying on geometric ray intersections. Consequently:

- Every selectable object must contribute a valid instance color.
- Point and line widths affect their visible picking footprint.
- Directional window selection compares colors within the rectangle with colors in the complete instance map to distinguish fully contained objects from intersections.

After changing scene hierarchy through an external integration, call
`viewer.refresh_hierarchy()` so object indices, transforms, settings, picking
colors, selection, and transform history remain synchronized. After changing
represented topology without changing the hierarchy, call
`viewer.refresh_geometry(...)` instead.

## UI components

Components wrap Qt widgets and share access to the active viewer through `Base`. Common bound controls include:

- `BooleanToggle`
- `ChoiceEdit`
- `ColorPicker`
- `NumberEdit`
- `TextEdit`

Commands that navigate the built-in sidebar use its closed domain API:

```python
viewer.ui.sidebar.set_current_tab("System")
viewer.ui.sidebar.focus_system_section("Camera")
```

`set_current_tab` accepts only `"Scene"`, `"Data"`, `"Annotations"`, or
`"System"`.
`focus_system_section` accepts only `"Camera"`, `"Display"`, or
`"Grid and Units"`, activates System, and focuses that section. Both
methods raise `ValueError` for unsupported identifiers. Components should use
this boundary instead of reaching into the sidebar's internal layouts.

`Container(..., compact=True)` applies the shared compact sidebar policy: content margins, row margins, spacing, size policy, and maximum row height. Use this for inspector-style forms instead of repeating layout constants.

The scene-object parameter dialog intentionally edits only writable scalar constructor parameters. Extend `ParameterForm` with explicit editors and conversion rules for structured values such as `Point`, `Vector`, `Frame`, and `Color`; do not parse arbitrary executable input.

`DatastructureAttributes` is an opt-in Viewer-owned inspector for element data;
it is not part of the default sidebar. Add `{"type":
"DatastructureAttributes"}` to `viewer.sidebar_items` before showing a custom
Viewer that requires it; the explicitly configured inspector appears in the
**Scene** domain. The inspector discovers the established Mesh and
Graph element APIs and uses ordered `default_*_attributes` dictionaries as its
column contract. Each tab uses a lazy `QAbstractTableModel`: it snapshots
element keys for row lookup but fetches cell values through singular attribute
accessors when Qt requests them.

Element edits and resets use singular setters and unsetters. Do not replace
them with bulk attribute methods: an empty bulk key collection can mean all
elements in the datastructure API. The component conservatively rebuilds render
data after successful mutations. Table selection remains local to the table;
viewport element selection and undo require their separately approved
architectures.

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
the declared paths they own and update immediately. `ViewerState` is not a
general extension namespace. Use `viewer.state` for supported runtime changes;
direct nested configuration assignment is intended for setup before
constructing the viewer, and replacing `viewer.config` is unsupported.

Bound controls that assign a configuration attribute before their callback can
call `viewer.state.notify(path)` to publish the resulting value.

For coupled settings, prefer a method on the owning runtime object. `Viewer.set_appearance`, renderer view changes, and grid rebuilding are examples of boundaries where a plain dataclass assignment is insufficient.

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
uv run ruff check .
uv run ruff format --check .
uv run pyright
QT_QPA_PLATFORM=offscreen uv run pytest -q
git diff --check
```

Build documentation changes strictly:

```bash
QT_QPA_PLATFORM=offscreen uv run mkdocs build --strict
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
