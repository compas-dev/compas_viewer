# Hello World

This tutorial creates a box and opens it in COMPAS Viewer.

## Install

COMPAS Viewer requires Python 3.12 or newer:

```bash
python -m pip install compas_viewer
```

## Create the script

Save the following as `hello_viewer.py`:

```python
from compas.geometry import Box
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add(Box(1.0), name="Hello, Viewer!")
viewer.show()
```

Run it:

```bash
python hello_viewer.py
```

A window opens with a box in the viewport and **Hello, Viewer!** in the scene tree.

The script has three essential steps:

1. Create the `Viewer`.
2. Add a COMPAS object to `viewer.scene`.
3. Call `viewer.show()` to open the interactive window.

Use the mouse wheel to zoom, right-drag to rotate, and left-click the box to select it. Press `H` if you need to frame the complete scene.

## Add another object

Add a point before `viewer.show()`:

```python
from compas.colors import Color
from compas.geometry import Point

viewer.scene.add(
    Point(0, 0, 1),
    name="Top point",
    pointcolor=Color.red(),
    pointsize=12,
)
```

Continue with the [user guide](user-guide.md) to learn about selection, object editing, configuration, images, and animation.
