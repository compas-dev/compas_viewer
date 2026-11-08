# Examples

Every Python file under `docs/examples/` is authoritative and is checked by
both Ruff and Pyright. The default category is **static-only interactive**:
the script constructs a viewer and ends with `viewer.show()`, so its visible
result is verified manually with a supported desktop OpenGL environment.

The following exceptions have additional runtime evidence:

- `object/points.py`, `scene/groups.py`, `configuration/window.py`,
  `dynamic/orbiting.py`, and the three `ui/` scripts form the representative
  **static-and-smoke** subset. The smoke test suppresses only the visible event
  loop and asserts the number of scene objects constructed by each complete
  script. Separate callback checks exercise render-data and transformation
  refreshes in the dynamic and side-dock examples.
- `object/brep.py` and `object/nurbs.py` are
  **static-plus-optional-runtime**. They use stable core COMPAS geometry
  facades and require compatible optional geometry backends, such as
  `compas_occ`, when executed.

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
