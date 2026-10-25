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
- Camera and Display tabs for view, grid, unit, color, and rendering settings.
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

## Inspect and edit objects

Select an object and open the **Object** tab to see:

- The scene-object name and type.
- Visibility and primitive display settings.
- Point, line, and face colors where supported.
- Point size, line width, and opacity.
- Constructor parameters detected on the underlying COMPAS data object.

Scene-object settings affect presentation. To edit the underlying geometry or data, select exactly one object and choose **Edit → Modify Parameters…**. The parameter form currently supports writable scalar values: booleans, integers, floating-point values, and strings. Applying a change regenerates the render data and bounding box.

Complex parameters such as frames and collections are displayed as information but are not yet editable through the generic parameter form. Modify those objects in Python and refresh or recreate their scene objects when needed.

## Add geometry from the UI

The **Add** menu creates commonly used defaults:

- Primitives: Point, Line, Frame, and Plane.
- Curves: Polyline, Polygon, Circle, and Ellipse.
- Surfaces: quad and saddle surfaces.
- Shapes: Box, Sphere, Cylinder, Cone, Capsule, and Torus.

The new object becomes the current selection and is framed automatically.

## Change appearance and display settings

Use **View → Appearance** to select:

- **System** to follow the operating-system appearance, including changes while the viewer is open.
- **Light** to force a light application palette.
- **Dark** to force a dark application palette.

The Display tab controls:

- Units: metres, centimetres, or millimetres.
- Shaded, lighted, ghosted, and wireframe rendering.
- Perspective, orthographic, and standard views.
- Viewport background and selection colors.
- Grid visibility, axes, mode, color, extents, and divisions.

Changing units rescales the grid and camera so that the scene remains usable at the selected scale.

## Configure the viewer in Python

Create a configuration before constructing the viewer:

```python
from compas_viewer import Viewer
from compas_viewer.config import Config

config = Config()
config.ui.appearance = "dark"
config.window.width = 1600
config.window.height = 900
config.renderer.show_grid = True
config.renderer.gridsize = (20.0, 20, 20.0, 20)
config.display.pointsize = 8.0

viewer = Viewer(config=config)
```

Save and restore settings as JSON:

```python
config.to_json("viewer-config.json")
restored = Config.from_json("viewer-config.json")
```

Configuration files contain persistent values only. Commands and menu callbacks are runtime extensions and are deliberately not serialized.

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
from compas_viewer import Viewer
from compas_viewer.scene import ArrowOverlay
from compas_viewer.scene import TextAnnotation

viewer = Viewer()
viewer.scene.add(
    ArrowOverlay(
        start=(0, 0, 0),
        end=(1, 1, 0),
        color=Color.red(),
        linewidth=4,
        on_top=True,
    )
)
viewer.scene.add(
    TextAnnotation(
        "Resultant force",
        position=(1, 1, 0),
        offset=(8, 8),
        backgroundcolor=Color(1, 1, 1, 0.8),
        padding=4,
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
