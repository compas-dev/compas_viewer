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
- A scene tree showing object hierarchy, groups, names, types, and visibility.
- An Object tab for information and display settings of the current selection.
- An Attributes tab for declared mesh and graph element attributes.
- Camera and Display tabs for view, grid, color, and rendering settings.
- Menus for creating geometry, selecting objects, changing the view, and loading or saving scenes.

The sidebar is visible by default. Use **View → Sidebar** to hide or restore it.

## Navigate the viewport

| Action | Input |
| --- | --- |
| Rotate | Right-drag |
| Pan | Shift + right-drag |
| Zoom | Mouse wheel |
| Zoom extents | `H` or **View → Zoom Extents** |
| Zoom selected | `F` or **View → Zoom Selected** |
| Set a standard view | **View → Set Current View** |

Zoom extents frames all visible objects. Zoom selected frames only the current selection.

## Select objects

| Action | Input |
| --- | --- |
| Replace the selection | Left-click an object |
| Add an object to the selection | Ctrl + left-click |
| Clear the selection | `Escape` |
| Delete selected objects | `Delete` |
| Rectangular selection | Shift + left-drag |

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

## Work with the scene tree

The scene tree mirrors parent-child relationships in the scene. Create explicit groups when related objects should appear under a shared node:

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

The **Add** menu creates commonly used defaults:

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
The available points are guidance markers. Only the distinct highlighted
winner inside the snapping radius and accepted by the depth test can be
selected. The guidance markers are not independently tested for occlusion.

After the first anchor is selected, its marker remains visible while the
available-point palette follows the next hovered object. Moving to the
background hides the palette. The live segment and formatted distance appear
when a second valid winner is available. Continuous line and edge locations
can still be selected, but displaying every such location as hover guidance is
deferred.

While a measurement is active, left-clicks belong to the measurement rather
than ordinary selection. Clicking the background does not create an anchor or
fall back to a construction plane. Right-drag rotation, Shift + right-drag
panning, and wheel zoom remain available. Press `Escape` or choose **Measure →
Cancel Measurement** to cancel the active interaction or a retained transient
inspection.

Snapping prefers points, mesh vertices, and graph nodes; then lines and edges;
then faces and surfaces. Fixed measurements accept every snap type.
Associative measurements support points, vertices and nodes with stable
serializable keys, and normalized positions on lines and edges. Faces and
surfaces are fixed-only in the initial implementation, so the Viewer shows a
rejection message instead of silently creating a fixed anchor. The supported
point guidance remains visible during that rejection, so the pointer can move
directly to a supported anchor.

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
associative interaction creates and selects one root-level
`compas.scene.DistanceDimension`, then deactivates the tool.
Completed dimensions remain visible when their world geometry coincides with
the measured geometry, while geometry closer to the camera still occludes
them.

See the [distance-measurement example](examples/ui/measurements.md) for a
step-by-step scene setup.

## Change appearance and display settings

Use **View → Appearance** to select:

- **System** to follow the operating-system appearance, including changes while the viewer is open.
- **Light** to force a light application palette.
- **Dark** to force a dark application palette.

The Display tab controls:

- Shaded, lighted, ghosted, and wireframe rendering.
- Perspective, orthographic, and standard views.
- Viewport background and selection colors.
- Grid visibility, axes, mode, color, extents, and divisions.

The **Units and Measurement** tab controls how measurements are presented:

- **Coordinate Unit** declares the unit suffix shown with measurement labels.
  Leaving it blank keeps the unit unspecified.
- **Display Precision** sets the number of decimal places shown.
- The active `compas.tolerance.TOL` values are shown read-only as process-wide
  numerical context.

The unit declaration does not convert coordinates, and display precision is
not a geometry tolerance. These presentation settings do not control snapping
or component association. A persistent dimension snapshots the unit and
precision when it is completed. A transient inspection uses the current
settings whenever it is drawn.

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

Configuration files contain persistent values only. Schema version 3 accepts
only declared fields. Loading schema-version-0, schema-version-1, and
schema-version-2 files retains supported values, discards the known retired
fields of the older schemas, and adds default measurement presentation.
Unknown fields are rejected. Commands and menu callbacks are runtime
extensions and are deliberately not serialized.

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
from compas.scene import ArrowAnnotation
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add(ArrowAnnotation((0, 0, 0), (1, 1, 0)))
viewer.scene.add(
    TextAnnotation(
        "Resultant force",
        anchor=(1, 1, 0),
        horizontal_alignment="center",
    )
)
viewer.scene.add(
    DistanceDimension(
        PointAnchor((0, 0, 0)),
        PointAnchor((1, 1, 0)),
        unit="m",
        precision=2,
    )
)
viewer.show()
```

See the [examples](examples.md) for geometry-specific display options, dynamic scenes, annotations, groups, and custom controls.

## Troubleshooting

If an object does not appear:

1. Use **Show All** and then **Zoom Extents**.
2. Confirm that the scene tree's Show checkbox is enabled.
3. Check that its point, line, or face display option is enabled.
4. Check that its color contrasts with the viewport background.
5. For custom types, confirm that a Viewer scene-object adapter is registered.

If selection is difficult for small points or thin lines, zoom closer or increase point size and line width temporarily.
