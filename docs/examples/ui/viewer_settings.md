# Viewer Settings and Content Domains

This example creates spatial objects, referenced data, and durable annotations,
then opens the modeless **Viewer Settings** window on **Camera**. It is also the
companion script for the [tutorial](../../tutorial.md).

```python
--8<-- "docs/examples/ui/viewer_settings.py"
```

Run the script and compare the two UI ownership areas:

1. Use **Scene**, **Data**, and **Annotations** in the right sidebar to inspect
   content. Data is read-only; deletion belongs only to Scene and Annotations.
2. Keep **Viewer Settings** open while orbiting or selecting in the main window.
3. Change Camera, Display, and Grid and Units values and observe live viewport
   feedback.
4. Close the settings window and choose **View → Viewer Settings…**. The same
   owned window is refreshed and reused.

With the Box selected in Scene, compare its editable declared general and
type-specific **Object Settings** with the read-only **Details** snapshot.
Details reports identity, general scene state, declared type-specific state,
and available represented-item parameters without invoking setters or refresh.
Then inspect the Box and Mesh rows in Data. Both report identity, binding, and
referrers. Every bound item exposes safe public-constructor parameters; Mesh
and Graph additionally expose ordered general datastructure attributes and
lazy read-only declared component tables. The [object inspection
example](object_inspection.md) demonstrates those combined read-only views,
shared references, defaults and local overrides, plus the separate opt-in
Scene component that edits declared element attributes.

The script passes `default_settings_items()` during `Viewer` construction to
show the setup-time composition boundary. The Viewer shallow-copies and
consumes those definitions while constructing the UI. Later mutations do not
recompose the existing window, and no live reload API is provided. Supply a
custom composition on the first `Viewer(...)` construction in the process;
later calls return the existing singleton and ignore new composition inputs. A
different composition requires a fresh process and application lifecycle.

Programmatic navigation supports exactly these calls:

```python
viewer.ui.settings.show()
viewer.ui.settings.show("Camera")
viewer.ui.settings.show("Display")
viewer.ui.settings.show("Grid and Units")
```

Unsupported identifiers and supported sections omitted from a custom
composition raise `ValueError`. Closing Viewer Settings hides it; closing the
main Viewer releases it. Window visibility, geometry, scroll position, and
focused section are transient and are not part of Viewer configuration or
scene serialization.

Manual native interaction is still required to assess platform focus behavior,
high-DPI presentation, and visual layout. The automated example checks cover
construction, composition, programmatic focus, reuse, and close-to-hide
behavior in an offscreen Qt environment.
