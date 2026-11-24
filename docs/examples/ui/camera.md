# Camera Controls

Set the initial camera and side-dock visibility through `Config`, then use
the **Camera** section of the modeless **Viewer Settings** window to change the
live camera vectors. **View → Viewer Settings…** opens the window; the Camera
Settings command opens the same reusable window focused on Camera. The example
also schedules that programmatic path after the main window appears. Both the
built-in controls and the custom side-dock sliders update the same camera
object and request live renderer feedback.

```python
--8<-- "docs/examples/ui/camera.py"
```
