# Examples

Every Python file under `docs/examples/` is authoritative and is checked by
both Ruff and Pyright. The default category is **static-only interactive**:
the script constructs a viewer and ends with `viewer.show()`, so its visible
result is verified manually with a supported desktop OpenGL environment.

The following exceptions have additional runtime evidence:

- `object/points.py`, `scene/groups.py`, `configuration/window.py`,
  `dynamic/orbiting.py`, `dynamic/transform.py`, and the representative `ui/`
  scripts
  form the representative **static-and-smoke** subset. The smoke test
  suppresses only the visible event loop and asserts the number of scene
  objects constructed by each complete script. Separate callback checks
  exercise categorized geometry, appearance, and transformation refreshes in
  the dynamic and side-dock examples. Focused composition checks additionally
  prove that the opt-in Attributes inspector and Viewer Settings example build
  their advertised UI rather than merely containing illustrative code.
- `object/brep.py` and `object/nurbs.py` are
  **static-plus-optional-runtime**. They use stable core COMPAS geometry
  facades and require compatible optional geometry backends, such as
  `compas_occ`, when executed.

The maintained coverage map is workflow-based rather than one example per API
symbol:

| Public area | Maintained examples |
| --- | --- |
| Scene, Data, Annotations, and inspection boundaries | [Viewer Settings and content domains](examples/ui/viewer_settings.md), [object and data inspection](examples/ui/object_inspection.md) |
| Viewer configuration and setup-time composition | [Viewer Settings and content domains](examples/ui/viewer_settings.md), [window configuration](examples/configuration/window.md) |
| Selection, transforms, and categorized refresh | [transformations](examples/dynamic/transform.md), [shared geometry updates](examples/dynamic/shared_geometry.md), [side-dock controls](examples/ui/sidedock.md) |
| Measurements and durable annotations | [distance measurements](examples/ui/measurements.md), [text annotations](examples/object/text_annotations.md), [scene groups](examples/scene/groups.md) |
| Scene and annotation serialization | [scene serialization](examples/scene/serialization.md) |
| Scale, legend, and screen-text overlays | [screen overlays](examples/ui/overlays.md) |
| Dynamic geometry and hierarchy changes | [dynamic examples](examples/dynamic.md), [dynamic scene changes](examples/scene/dynamic_scene.md) |
| Optional geometry backends | [Brep](examples/object/brep.md), [NURBS](examples/object/nurbs.md) |

The headless suite proves construction, round trips, callbacks, and advertised
UI composition. It does not prove native OpenGL output, picking, focus,
scrolling, animation cadence, visual placement, or high-DPI presentation.
Those outcomes require a supported native desktop renderer. Optional-backend
examples remain statically checked when their declared backend is unavailable.

Run the representative headless subset with:

```bash
QT_QPA_PLATFORM=offscreen uv run pytest tests/test_documentation_examples.py
```

Drafts and archived examples are kept outside `docs/examples/`; they are not
published or silently excluded from the static gate.

- [Object examples](examples/object.md)
- [Scene examples](examples/scene.md)
- [Color examples](examples/color.md)
- [Dynamic examples](examples/dynamic.md)
- [UI examples](examples/ui.md)
- [Configuration examples](examples/configuration.md)
