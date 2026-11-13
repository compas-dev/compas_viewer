# User Guide

This guide explains how to create, inspect, navigate, edit, and export a COMPAS Viewer scene. It is intended for people using the viewer interactively or from a Python script. For extending the viewer itself, see the [developer guide](developer-guide.md).

## Create a viewer

Install the package in a Python 3.12 or newer environment:

```bash
python -m pip install compas_viewer
```

Create a viewer, add COMPAS objects to its scene, and open the interactive window:

```python
from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Point
from compas.geometry import Sphere
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add(Box(2.0), name="Building volume")
viewer.scene.add(Sphere(0.5), name="Reference sphere", facecolor=Color(0.2, 0.6, 0.9))
viewer.scene.add(Point(0, 0, 2), name="Survey point", pointsize=12)
viewer.show()
```

`viewer.scene.add(...)` returns the scene object that represents the supplied data. Keep that reference when you want to change its display or transformation later.

## Understand the interface

The main window consists of:

- A 3D viewport for navigation and selection.
- A **Scene** sidebar tab with the spatial hierarchy and details for the
  selected spatial object.
- A **Data** sidebar tab with one row per distinct data item referenced by the
  scene or its annotations.
- An **Annotations** sidebar tab with the ordered annotation list and details
  for the selected annotation.
- A **System** sidebar tab with Camera, Display, and Grid and Units
  sections.
- A visible toolbar with zoom, capture, and measurement controls.
- A grouped **View** control over the top-right of the viewport for standard
  views and render modes.
- Menus for creating Scene geometry, selecting objects, changing the view, and loading or saving scenes.

The sidebar and toolbar are visible by default. Use **View → Sidebar** or
**View → Toolbar** to hide or restore them.

## Navigate the viewport

| Action | Input |
| --- | --- |
| Rotate | Right-drag |
| Pan | Shift + right-drag |
| Zoom | Mouse wheel |
| Zoom extents | Toolbar **Zoom Extents**, `H`, or **View → Zoom Extents** |
| Zoom selected | Toolbar **Zoom Selected**, `F`, or **View → Zoom Selected** |
| Set a standard view | The viewport **View** menu's View group; or **View → Set Current View** |
| Set the render mode | The viewport **View** menu's View Mode group; or **View → Set Render Mode** |

Zoom extents frames all visible objects. Zoom selected frames only the current selection.
The grouped viewport menu keeps Perspective, Top, Front, Right, and Ortho
under **View**, and Shaded, Lighted, Ghosted, and Wireframe under **View
Mode**. Each group shows its current checked choice. Closing the menu returns
focus to the viewport, so orbit, pan, zoom, and renderer shortcuts remain
immediately available.

## Select objects

| Action | Input |
| --- | --- |
| Replace the selection | Left-click an object |
| Add an object to the selection | Ctrl + left-click |
| Clear spatial and annotation selection | Click empty viewport background or press `Escape` |
| Delete the active domain's selection | `Delete` or **Edit → Delete Selected** |
| Rectangular selection | Shift + left-drag |

When no measurement tool is active, an unmodified click on empty viewport
background clears both spatial and annotation selection. Ctrl-clicking empty
background leaves both selections unchanged. If a measurement is active,
`Escape` cancels the measurement first and leaves selection unchanged; press it
again to clear both selections.

Rectangular selection is directional:

- Drag from left to right to select only objects fully contained by the rectangle.
- Drag from right to left to select every object intersecting the rectangle.

The **Select** menu also provides Select All, Select Inverted, and selection by object type, display color, or name. **Isolate Selected** hides everything else and frames the selected objects. **Show All** restores all scene objects.

Scripts can use the same ordered selection as the viewport and scene tree:

```python
box = viewer.scene.add(Box(2.0), name="Box")
sphere = viewer.scene.add(Sphere(1.0), name="Sphere")

viewer.state.selection.replace((box, sphere))
viewer.state.selection.remove(box)

print(viewer.state.selection.objects)
```

The selection also provides `add`, `toggle`, and `clear`. Every selected object
must belong to the Viewer's current scene. Replacing the scene or removing an
object removes the corresponding transient selection; saved scenes do not
contain selection state.

Spatial and annotation selections are independent and may both contain values.
Changing sidebar tabs preserves both selections. Picking in the viewport or
Scene tree changes only spatial selection; selecting an entry in Annotations
changes only annotation selection.

The **Data** tab is a flat, read-only view of the current scene's referenced
items. Shared items appear once with their number of references; unresolved
references remain visible without being loaded. Select a row and use
**Details** to inspect its GUID, binding status, referrers, and public
parameters. Mesh and Graph details expose their declared element-attribute
tables lazily and read-only. Data-row selection is temporary and independent
from Scene and Annotations selection.

Delete follows the active interaction domain and never removes both selections.
Focus in the Scene tree or viewport removes spatial objects; focus in the
annotation list or details removes annotations. Menu activation follows the
active sidebar tab. The action is disabled in System, and text or numeric
editors retain their local Delete behavior.

Deleting a selected group removes its complete scene subtree but does not
delete the independently owned geometry or data. Deletion is not part of the
transform-only undo history and clears that history. Associative dimensions
that reference a removed object remain in the scene and become unresolved;
they are not silently converted or deleted.

## Work with the scene tree

The scene tree in the **Scene** tab mirrors parent-child relationships in the
scene. The detail area below it shows controls for the selected spatial object.
Drag the Scene splitter to resize the hierarchy and detail areas; this does not
resize the independent Annotations splitter. The details area no longer keeps
a large inline description open. Select one or more objects and choose
**Details** for a read-only modal snapshot of names, types, visibility, and
available represented-object parameters. Editable controls remain in the
sidebar, and Details is disabled when nothing is selected. Parametric
representations expose **U Resolution** and, where used, **V Resolution** in
this area: cones and cylinders use U; spheres, tori, and capsules use U and V;
parametric surfaces use both; boxes and unrecognized shapes expose neither.
Shape resolution is at least 3, surface resolution is at least 1, and capsule
V resolution is at least 4 and even. Rejected edits restore the previous value.
For shapes and surfaces, the line controls are labelled **Show wireframe**,
**Wireframe color**, and **Wireframe width**; meshes and graphs continue to use
edge terminology. Toggling these display settings does not regenerate the
parametric representation, including at high resolution.
Create explicit groups when related objects should appear under a shared node:

```python
from compas.geometry import Point
from compas_viewer import Viewer

viewer = Viewer()
group = viewer.scene.add_group("Supports")

for index, xyz in enumerate([(0, 0, 0), (4, 0, 0), (4, 4, 0), (0, 4, 0)]):
    viewer.scene.add(Point(xyz[0], xyz[1], xyz[2]), parent=group, name=f"Support {index + 1}")

viewer.show()
```

The Show column changes an object's visibility without removing it. Selection in the tree and selection in the viewport remain synchronized.

## Transform objects and undo

Use `transform_objects` when a script, command, or interactive tool should move
one or more scene objects and make that change reversible:

```python
from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()
first = viewer.scene.add(Box(1.0))
second = viewer.scene.add(
    Box(1.0),
    transformation=Translation.from_vector([3.0, 0.0, 0.0]),
)

viewer.transform_objects(
    (first, second),
    Translation.from_vector([0.0, 0.0, 2.0]),
)
viewer.undo()
viewer.redo()
```

The transformation is a world-space delta applied to every object's original
world transformation. The Viewer converts each result back to a local
transformation through its parent. Every target must belong to the current
scene. An operation containing both an ancestor and its descendant is rejected,
and any invalid target leaves all objects unchanged. Only `space="world"` is
currently supported.

Undo and redo cover explicit Viewer transform transactions only. They do not
capture arbitrary scene edits, geometry mutations, object-inspector changes, or
datastructure attribute edits. A new transform after undo clears the redo
history. **Edit → Undo** and **Edit → Redo** use the same transaction history as
the programmatic methods.

Direct scene-object or represented-data mutation remains valid, but the Viewer
cannot detect it automatically. Call the matching explicit refresh operation:

| Change | Operation |
| --- | --- |
| Coordinates, topology, or represented geometry | `viewer.refresh_geometry(objects)` |
| Colors, visibility, opacity, or display sizes | `viewer.refresh_appearance(objects)` |
| Direct local or world transformation assignment | `viewer.refresh_transform(objects)` |
| Added, removed, or reparented scene objects | `viewer.refresh_hierarchy()` |

Omit `objects` to refresh every object in the current scene. Transform refresh
updates transformation data and world bounds without rebuilding geometry.
Because it reports an external, untracked transformation change, it clears the
Viewer's transform history. Hierarchy refresh also clears transform history;
geometry and appearance refresh do not.

## Save and restore scenes

A serialized scene contains the hierarchy, references to COMPAS data by GUID,
and durable presentation state. It does not embed the referenced geometry or
data structures. Save those objects separately when they must be restored with
the scene.

After loading, the scene nodes are available for inspection without the data.
Bind the independently loaded objects with `scene.bind(...)` or
`scene.bind_many(...)`, then assign the scene to the Viewer. The stable scene
objects keep their identity; the Viewer creates transient render state only
when it prepares or draws the scene. Accessing an unresolved item or drawing
before all referenced items are bound raises `SceneItemNotBoundError`.

Durable Viewer state includes transformations, visibility, colors, display
sizes, resolution, and mesh display flags. Selection, instance-picking colors,
GPU buffers, and renderer caches belong to the live Viewer session and are not
serialized. See the [scene serialization example](examples/scene/serialization.md)
for the complete step-by-step script.

## Inspect and edit objects

Select an object and open the **Object** tab to see:

- The scene-object name and type.
- Visibility and primitive display settings.
- Point, line, and face colors where supported.
- Point size, line width, and opacity.
- Constructor parameters detected on the underlying COMPAS data object.

Scene-object settings affect presentation. To edit the underlying geometry or data, select exactly one object and choose **Edit → Modify Parameters…**. The parameter form currently supports writable scalar values: booleans, integers, floating-point values, and strings. Applying a change regenerates the render data and bounding box.

Complex parameters such as frames and collections are displayed as information but are not yet editable through the generic parameter form. Modify those objects in Python and call `refresh_geometry` for the affected scene objects when needed.

## Edit datastructure element attributes

Select one mesh or graph and open the **Attributes** tab. The Viewer creates a
separate table for each element domain that declares default attributes:

- Mesh vertices, edges, and faces.
- Graph nodes and edges.

The first column contains the element key. The remaining columns follow the
insertion order of the corresponding `default_*_attributes` dictionary. Values
are fetched as the table displays them, so the Viewer does not create a widget
for every cell or copy the complete attribute data.

Boolean, integer, floating-point, and text defaults define editable columns.
Columns with `None` or structured defaults remain visible and read-only. Select
one or more editable cells and choose **Reset to default** to remove their
explicit overrides and expose the effective default values again.

Only attributes declared in the default dictionaries appear. Sparse attributes
that exist on individual elements, the default dictionaries themselves, batch
paste, and synchronized viewport element selection are outside the initial
table contract. Attribute-table edits do not enter the Viewer's transform-only
undo history. Successful edits rebuild the selected object's render data and
refresh the Viewer.

## Add geometry from the UI

**Scene → Add** creates commonly used defaults:

- Primitives: Point, Line, Frame, and Plane.
- Curves: Polyline, Polygon, Circle, and Ellipse.
- Surfaces: quad and saddle surfaces.
- Shapes: Box, Sphere, Cylinder, Cone, Capsule, and Torus.

The new object becomes the current selection and is framed automatically.

## Measure distances

Use the **Measure** menu to start one of three one-shot interactions:

| Action | Result |
| --- | --- |
| **Inspect Distance** | Keeps a transient distance in the Viewer without changing the scene or selection. |
| **Add Fixed Distance Dimension** | Adds a persistent dimension containing two copied world-coordinate points. |
| **Add Associative Distance Dimension** | Adds a persistent dimension linked to supported scene components. |

Move the pointer over an object, then left-click two anchors. While a
measurement is active, hovering a Point, Mesh, or Graph displays all of that
object's discrete point snaps: the Point itself, Mesh vertices, or Graph nodes.
The available points are bright hollow square guidance markers. Only the
distinct filled winner inside the snapping radius and accepted by the depth
test can be selected. The guidance markers are not independently tested for
occlusion. During measurement, Mesh vertices use a measurement-only point
footprint in the acquisition pass, including when ordinary vertex glyphs are
hidden. This footprint never appears in normal rendering. Winner visibility
therefore avoids unreliable single-pixel depth comparisons at receding
vertices without admitting background pixels or other objects.

After the first anchor is selected, its marker remains visible while the
available-point palette follows the next hovered object. Moving to the
background hides the palette. The live segment and formatted distance appear
when a second valid winner is available. The 18-logical-pixel acquisition
radius provides a pronounced but deterministic lock to the nearest eligible
point.

Only displayed discrete guidance is snappable: Point objects, Mesh vertices,
and Graph nodes. A Mesh may expose all vertices as measurement guides while its
ordinary vertex glyphs are off, provided a face or edge representation keeps
the Mesh visibly represented. Hidden objects and Meshes with no visible
representation remain excluded. Lines, edges, faces, and surfaces are not
themselves candidates. A miss creates no anchor rather than silently accepting
unmarked geometry.

While a measurement is active, left-clicks belong to the measurement rather
than ordinary selection. Clicking the background does not create an anchor or
fall back to a construction plane. Right-drag rotation, Shift + right-drag
panning, and wheel zoom remain available. Press `Escape` or choose **Measure →
Cancel Measurement** to cancel the active interaction or a retained transient
inspection.

Fixed measurements copy the selected point, vertex, or node coordinates.
Associative measurements link to the same displayed components using stable
serializable keys. The acquisition targets are identical; only persistence
differs.

The equivalent Python entry points are:

```python
viewer.start_distance_inspection()
viewer.start_distance_dimension(mode="fixed")
viewer.start_distance_dimension(mode="associative")
viewer.cancel_measurement()
```

Starting a new mode clears the previous transient result. A completed
inspection remains Viewer-owned: it is not a scene object, is not selected or
serialized, and does not enter transform history. A completed fixed or
associative interaction creates and selects one `compas.scene.DistanceDimension`
entry in the flat annotation collection, then deactivates the tool. Annotation
selection is independent from spatial object selection.
Completed dimensions render in a separate final annotation pass without depth
testing or depth writes, so scene geometry cannot hide them.

See the [distance-measurement example](examples/ui/measurements.md) for a
step-by-step scene setup.

## Inspect area and volume

Area and volume are transient properties of one selected spatial object. Select
exactly one object, then choose **Measure → Inspect Selected Area** or
**Measure → Inspect Selected Volume**. The Viewer displays one read-only result
and retains no measurement state, annotation, or scene data. Starting either
inspection cancels an active or retained distance inspection.

The represented item must provide a public `area` or `volume` method or
property. Open meshes do not enclose a measurable volume. Unsupported items,
unresolved scene references, invalid scalar results, and unsupported
transformations produce an explicit error; the Viewer never substitutes a
render tessellation.

Area is exact for rigid, reflected, and uniformly scaled world
transformations. Non-uniform scale, shear, and projective transforms are
rejected because a local scalar does not contain enough information for an
exact transformed surface area. Volume is exact for affine transformations,
including non-uniform scale and shear, and is multiplied by the absolute
determinant of the transformation's linear part. Projective transforms are
rejected.

The same operations are available from Python:

```python
from compas.geometry import Box
from compas_viewer import Viewer

viewer = Viewer()
box = viewer.scene.add(Box(2.0), name="Box")
viewer.state.selection.replace((box,))

area = viewer.inspect_selected_area()
volume = viewer.inspect_selected_volume()

print(area)
print(volume)
```

The methods return world-coordinate scalars. Result dialogs use the current
display precision and append the declared coordinate unit as `unit²` or
`unit³`; no unit conversion is performed.

## Change appearance and display settings

Use **View → Appearance** to select:

- **System** to follow the operating-system color scheme, including changes while the viewer is open.
- **Light** to force the light COMPAS Viewer palette.
- **Dark** to force the dark COMPAS Viewer palette.

These choices style the Viewer application chrome and select the automatic
Viewer content palette. An automatic viewport follows the effective light or
dark scheme. New Viewer scene objects resolve omitted presentation colors from
that scheme when they are created; the resulting concrete colors do not change
if the appearance changes later. Explicit and deserialized colors remain
authoritative and are never recolored.

| Content role | Light | Dark |
| --- | --- | --- |
| Viewport | `#FAFAFA` | `#10161B` |
| Surface and face | `#D8DEE4` | `#3A4650` |
| Line and edge | `#4B5563` | `#B8C2CC` |
| Point and vertex | `#111827` | `#F2F6F8` |

`config.renderer.backgroundcolor = None` selects the automatic viewport.
Assigning a `Color` makes the background explicit, so later appearance changes
do not alter it. Grid, selection, explicit scene-object appearance, existing
annotations, legends, and overlays retain their existing ownership.

The **Display** section of the **System** tab controls:

- Shaded, lighted, ghosted, and wireframe rendering.
- Perspective, orthographic, and standard views.
- Viewport background and selection colors.

The visible toolbar provides **Zoom Selected**, **Zoom Extents**, **Capture
View**, and one **Measurement** menu. The measurement menu starts distance
inspection, creates fixed or associative distance dimensions, or cancels the
active measurement. The grouped viewport menu owns the standard-view and
render-mode choices. Changes through that menu, the application View menu,
Display section, or Python API update every other surface. Set
`config.ui.toolbar.show = False` before constructing the Viewer to start with
the toolbar hidden.

The **Grid and Units** section of the **System** tab controls:

- Grid visibility, axes, mode, color, extents, and divisions.
- **Coordinate Unit** declares the unit suffix shown with measurement labels.
  Leaving it blank keeps the unit unspecified.
- **Display Precision** sets 0–15 decimal places for displayed measurements.

The unit declaration does not convert coordinates, and display precision is
not a geometry tolerance. These presentation settings do not control snapping
or component association, and the unit does not change grid spacing. Global
`compas.tolerance.TOL` remains available to computational code but is not a
Viewer control or System-sidebar field. A persistent dimension snapshots the
unit and precision when it is completed. A transient inspection uses the
current settings whenever it is drawn. Later Grid and Units changes affect
only transient measurements and dimensions created afterward; they do not
rewrite existing dimensions.

Camera, Display, and Grid and Units use the same two-column field layout:
labels are left-aligned and editors share one right-hand column.

The Camera section is fully populated when the System panel first appears; it
does not require a later refresh or resize to reveal its controls.

## Configure the viewer in Python

Create a configuration before constructing the viewer:

```python
from compas_viewer import Viewer
from compas_viewer.config import Config

config = Config()
config.ui.appearance = "dark"
config.window.title = "My COMPAS Viewer"
config.window.width = 1600
config.window.height = 900
config.renderer.show_grid = True
config.renderer.gridsize = (20.0, 20, 20.0, 20)
config.measurement.unit = "mm"
config.measurement.precision = 3

viewer = Viewer(config=config)
```

The configured window title also supplies the Qt application name and display
name. Set `config.window.fullscreen = True` to start fullscreen. The packaged
COMPAS icon is used by default; `config.window.icon` may point to an existing
absolute icon path. These identity settings are applied during Viewer startup
and are not a live-update interface.

Configuration is a setup-time interface. Adjust its nested fields before
constructing the Viewer; replacing `viewer.config` is unsupported. Runtime UI
changes use the Viewer's commands and state interfaces instead.

Save and restore settings as JSON:

```python
config.to_json("viewer-config.json")
restored = Config.from_json("viewer-config.json")
```

Configuration files contain persistent values only. Schema version 4 accepts
only declared fields and uses `renderer.backgroundcolor=None` as the automatic
viewport marker. Loading schema-version-0 through schema-version-3 files
retains supported values and discards only known retired fields. A schema-3
background remains explicit; if it was omitted, migration records the former
`#D8DDE2` default explicitly rather than guessing that it should become
automatic. Unknown fields are rejected. Commands and menu callbacks are
runtime extensions and are deliberately not serialized.

## Load, save, and capture

Use the **Scene** menu to load or save COMPAS JSON data. The viewer accepts serialized scenes, supported geometry, data structures, and lists of supported objects.

Use **View → Capture View** for an interactive screenshot. From Python, render an image without entering the visible viewer event loop:

```python
from compas.geometry import Sphere
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add(Sphere(1.0))
viewer.save_image("sphere.png", width=1600, height=900, zoom_extents=True)
```

The filename suffix selects the image format.

## Record an animation

`record_animation` calls an update function before rendering each frame:

```python
from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()
box = viewer.scene.add(Box(1.0))

def update(frame):
    box.transformation = Translation.from_vector([0.02 * frame, 0, 0])
    viewer.refresh_transform((box,))

viewer.record_animation(
    "moving-box.gif",
    update=update,
    frames=120,
    preset="documentation",
    zoom_extents=True,
)
```

Available presets are:

| Preset | Size | FPS | Typical use |
| --- | --- | ---: | --- |
| `preview` | 640 × 360 | 15 | Quick iteration |
| `documentation` | 960 × 540 | 24 | Documentation and web pages |
| `presentation` | 1280 × 720 | 30 | Presentations and demos |

GIF and animated WebP output are supported. Pass `width`, `height`, or `fps` to override an individual preset value.

## Add annotations

Text and arrow annotations remain legible as the camera changes:

```python
from compas.colors import Color
from compas.scene import ArrowAnnotation
from compas.scene import DimensionStyle
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add_annotation(ArrowAnnotation((0, 0, 0), (1, 1, 0)), name="Force direction")
viewer.scene.add_annotation(
    TextAnnotation(
        "Resultant force",
        anchor=(1, 1, 0),
        horizontal_alignment="center",
    ),
    name="Force label",
    label_background=Color(0.05, 0.05, 0.05, 0.75),
    label_background_padding=3.0,
)
viewer.scene.add_annotation(
    DistanceDimension(
        PointAnchor((0, 0, 0)),
        PointAnchor((1, 1, 0)),
        unit="m",
        precision=2,
    ),
    name="Force length",
    style=DimensionStyle(
        color=Color.red(),
        line_width=4.0,
        extension_line_width=1.0,
        text_size=14.0,
        arrow_size=12.0,
        label_offset=8.0,
    ),
    label_background=Color.white(),
    label_background_padding=2.0,
)
viewer.show()
```

Annotations live in `viewer.scene.annotations`, not in the spatial scene tree.
They have no parent, children, or inherited transformation. The
**Annotations** tab lists them in collection order. Drag its splitter to resize
the annotation list and dimension-details areas independently of the Scene
tab. When the details area is shorter than its controls, scroll vertically;
the controls retain their natural size and spacing. Select exactly one entry to
show an explicit Name field, its read-only Type, and, for a distance dimension,
separate **Measurement Format** and **Dimension Style** groups. Measurement
Format edits the dimension's **Coordinate Unit** and **Display Precision**;
Dimension Style edits color, dimension-line width, extension-line width, text
size, arrow size, and label offset. A **Spatial Layout** group edits a signed world-space offset and an
optional world-space plane normal. Leave all three normal components blank for
no normal, or provide three finite values. The read-only status explains
whether the durable layout resolves. Keyboard traversal retains the complete
draft until **Apply Layout** validates and replaces it atomically; **Reset
Layout** restores zero offset and no normal. Valid application refreshes only
the selected annotation. A **Label
Background** group for a selected text or distance annotation
provides **Enable Background**, an alpha-aware color editor, and nonnegative
logical-pixel padding. Disabling it stores `None`. Multiple selection shows a
summary and removal controls instead of a single-entry form. Style sizes,
offsets, and label padding use logical screen pixels.

Coordinate Unit input is trimmed; leaving it blank stores no unit. Display
Precision is an integer from 0 through 15 inclusive. Values outside that range
are rejected rather than clamped or truncated. These edits refresh only the
selected annotation and never convert coordinates, rescale anchors, or change
the measured distance. An explicit dimension label remains verbatim and takes
precedence, so format edits may not change visible text until that explicit
label is removed; the override does not relax validation. The controls remain
available when an associative dimension's geometric anchors are unresolved,
but they are hidden for no selection, multiple selection, text or arrow
annotations, and unresolved annotation data bindings.

A nonzero spatial offset displaces the dimension line along the normalized
cross product of the stored plane normal and the measured segment. Extension
lines connect the measured anchors to the displaced endpoints. Missing, zero,
or parallel normals leave the ordinary zero-offset line visible when both
anchors resolve; Viewer never substitutes a camera-facing direction. If an
associative anchor is unresolved, no cached or synthesized dimension line is
drawn. Interactive dragging and reusable construction planes are not part of
this initial editing workflow.

New persistent distance dimensions acquired through Viewer enable a label
background by default: `#FAFAFAE6` in the light scheme and `#10161BE6` in the
dark scheme, with two logical pixels of padding. The color is resolved when
the dimension is created and does not change later. Existing dimensions,
programmatic annotation insertion, and explicitly supplied values remain
unchanged.

Text and distance entries may define `label_background` and a nonnegative
`label_background_padding` in logical pixels. `None` keeps the default
transparent result, and the color alpha controls opacity. Viewer draws the
background behind the glyphs and, for dimensions, in front of the dimension
line. The Annotations details controls edit these same durable fields and
refresh only the affected annotation. Arrow annotations have no label and
therefore accept only the default background values and do not show the group.

Pressing `Delete` while the annotation list or annotation details has focus
removes selected annotations only. The same command removes spatial objects
when focus is in the Scene tree or viewport. **Edit → Delete Selected** follows
the active Scene or Annotations tab and is disabled in System. Neither path
crosses into the other collection.

Scripts use `viewer.state.annotation_selection` for annotations and
`viewer.state.selection` for spatial objects. Removing a spatial object does
not cascade to an associative dimension that references it; the dimension
remains present and displays an unresolved state.

See the [examples](examples.md) for geometry-specific display options, dynamic scenes, annotations, groups, and custom controls.

## Troubleshooting

If an object does not appear:

1. Use **Show All** and then **Zoom Extents**.
2. Confirm that the scene tree's Show checkbox is enabled.
3. Check that its point, line, or face display option is enabled.
4. Check that its color contrasts with the viewport background.
5. For custom types, confirm that a Viewer scene-object adapter is registered.

If selection is difficult for small points or thin lines, zoom closer or increase point size and line width temporarily.
