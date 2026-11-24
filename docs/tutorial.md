# Tutorial: Explore and Configure a Viewer

This tutorial builds one small scene and uses it to tour the Viewer domains,
settings, annotations, and measurement workflow. Complete [Hello
World](hello-world.md) first if you have not opened a Viewer yet.

## Build the scene

The complete script is published with the examples and checked by Ruff,
Pyright, and the documentation smoke tests:

```python
--8<-- "docs/examples/ui/viewer_settings.py"
```

Run it with Python 3.12 or newer in an environment containing `compas` and
`compas_viewer`:

```bash
python docs/examples/ui/viewer_settings.py
```

The script does four setup tasks before opening the event loop:

1. It configures the initial camera, viewport, and measurement presentation.
2. It creates a Box and a Mesh, so the scene contains both geometry and a
   datastructure.
3. It adds a text annotation and a durable distance dimension.
4. It schedules the modeless Viewer Settings window to open on **Camera** after
   the main window appears.

`settings_items` is a setup-time composition input. The Viewer shallow-copies
the supplied definitions and consumes them while constructing its UI. Mutating
the original list or `viewer.settings_items` afterward does not rebuild the
window. Supply composition on the first `Viewer(...)` construction in a
process. Later `Viewer(...)` calls return the existing singleton and ignore new
composition inputs. A different composition therefore requires a fresh process
and application lifecycle unless a future reset mechanism is approved.

## Explore the three content domains

The right sidebar contains exactly three domains:

- **Scene** is the spatial hierarchy. Select the Box or Mesh here, or select it
  directly in the viewport.
- **Data** is a read-only, GUID-deduplicated projection of the data referenced
  by scene objects and annotations. Open a row to inspect it. Data does not
  load, edit, delete, resolve, or own the represented value.
- **Annotations** contains the durable label and distance dimension. Annotation
  selection is independent from spatial-object selection.

The **Delete Selected** command is enabled only when Scene or Annotations owns
the active context. It is disabled in Data. Programmatic navigation uses the
same closed domain names:

```python
viewer.ui.sidebar.set_current_tab("Scene")
viewer.ui.sidebar.set_current_tab("Data")
viewer.ui.sidebar.set_current_tab("Annotations")
```

Any other identifier raises `ValueError`.

### Inspect Scene objects and referenced Data

Select one spatial object in **Scene**. **Object Settings** shows the editable
declared general and type-specific settings for that object, such as name,
visibility, opacity, and supported display colors and sizes. Mesh and Graph
objects use edge terminology, while shapes and surfaces expose wireframe
controls; only parametric producers that consume resolution expose U or V
resolution. These controls are not a complete dump of object state, and
component-specific fields are not fabricated for unsupported object types.

Choose **Details** for a read-only snapshot. A single selection reports stable
identity, general scene state, fields declared by that concrete scene-object
type, and available represented-item parameters. It includes declared fields
that have no generic editor, but it does not discover arbitrary Python
properties. Multiple selections retain the compact count, type, and name
summary. Use **Edit → Modify Parameters…** for the separate, writable
scalar-parameter path. Structured parameters remain informational unless a
dedicated editor exists.

Now select rows in **Data** and choose **Details**. Every row reports identity,
binding status, and referrers. Every bound item has a **Parameters** tab for
safe public-constructor attributes. Every Core `Datastructure` adds **General
Attributes** for its ordered public `attributes` mapping. Mesh and Graph then
add lazy read-only component tabs: Vertices, Edges, and Faces for Mesh; Nodes
and Edges for Graph. Component columns come from declared defaults, so
effective defaults and local overrides are visible while sparse undeclared
attributes remain omitted. These tabs inspect one shared referenced item; they
are not an editing or ownership surface. An unresolved row remains
metadata-only and does not trigger loading or resolution.

The opt-in **Attributes** inspector demonstrated by [Object and data
inspection](examples/ui/object_inspection.md) is different. It is a
Scene-selection component for editing declared Mesh or Graph attributes and
must be included in the setup-time sidebar composition. Data Details never
enables those edits.

## Use Viewer Settings

Choose **View → Viewer Settings…** to open the same window used by the script.
It contains **Camera**, **Display**, and **Grid and Units**. Because the window
is modeless, keep it open while orbiting, panning, zooming, selecting content,
or comparing display changes in the viewport.

The programmatic API can open the window generally or focus one section:

```python
viewer.ui.settings.show()
viewer.ui.settings.show("Camera")
viewer.ui.settings.show("Display")
viewer.ui.settings.show("Grid and Units")
```

Opening refreshes all configured controls from current Viewer state and reuses
the one window owned by that Viewer. Closing the settings window hides it;
opening it again reuses the same surface. Closing the main Viewer releases the
owned settings resources. Visibility, geometry, scroll position, and focused
section are transient UI state and are not serialized.

Only `None`, `"Camera"`, `"Display"`, and `"Grid and Units"` are supported.
An unsupported name, or a supported section omitted from a custom setup-time
composition, raises `ValueError`.

Escape follows the active interaction context:

- With Viewer Settings active, window-level `Escape` hides only that window.
- A focused editor or open combo box keeps `Escape` local.
- With the main Viewer active, `Escape` cancels an active measurement first;
  otherwise it clears content selection. A merely visible settings window does
  not intercept it.

## Inspect and edit durable annotations

Select **Tutorial distance** in Annotations. Its details expose the persisted
unit and precision snapshot, visual style, and spatial-layout controls. The
dimension in the script uses fixed anchors, so later object transforms do not
move its endpoints.

To create another dimension interactively, choose **Measure → Add Fixed
Distance Dimension**, then click two highlighted eligible points. Use
**Associative** mode when the anchors should follow supported referenced Mesh
vertices or Graph nodes. A background click never creates an unmarked anchor.
The [distance measurement example](examples/ui/measurements.md) covers snapping,
fixed and associative ownership, validation, and rendering in detail.

**Grid and Units** controls presentation defaults for transient measurements
and dimensions created afterward. It does not convert coordinates or rewrite
the stored format of existing dimensions.

## Continue through the feature examples

The tutorial intentionally keeps one small scene. Continue with the focused
examples for the remaining public workflows:

- [Object and data inspection](examples/ui/object_inspection.md)
- [Scene groups and annotations](examples/scene/groups.md)
- [Scene serialization](examples/scene/serialization.md)
- [Dynamic scene changes](examples/scene/dynamic_scene.md)
- [Transformations and refresh categories](examples/dynamic/transform.md)
- [Scale and legend overlays](examples/ui/overlays.md)
- [Viewer configuration](examples/configuration/window.md)

The [user guide](user-guide.md) is the behavioral reference. Contributors and
plugin authors should continue with the [developer guide](developer-guide.md).
