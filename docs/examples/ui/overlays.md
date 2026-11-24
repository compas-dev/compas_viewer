# Screen Overlays

Add transient screen information directly to the Viewer. Overlays are drawn in
the order in which they are added. They do not become scene objects and are not
saved with the scene.

The scale bar is exact throughout an orthographic view. In a perspective view,
it reports scale at the camera-target depth and states this limitation in its
label.

`ScreenTextOverlay` uses normalized viewport coordinates: `(0, 0)` is the
top-left corner and `(1, 1)` is the bottom-right. Its alignment selects which
part of the text is placed at that point. Screen text remains fixed when the
camera changes and keeps its relative location when the viewport is resized.

The example also adds and removes a temporary note. Screen text is
programmatic only: it has no interactive placement or management UI and is not
saved with the scene.

```python
--8<-- "docs/examples/ui/overlays.py"
```
