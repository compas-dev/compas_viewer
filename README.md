# COMPAS VIEWER

A standalone, high-performance 3D viewer for COMPAS 2.0, built with PySide6 and OpenGL.

[![Version](https://img.shields.io/badge/version-1.6.0-blue.svg)](https://github.com/compas-dev/compas_viewer)
[![Documentation](https://img.shields.io/badge/docs-compas.dev-green.svg)](https://compas.dev/compas_viewer/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

More information is available in the docs: <https://compas.dev/compas_viewer/>

## Features

### Core Functionality
- **High-Performance Rendering**: Modern OpenGL 3.3 Core Profile with optimized buffer management and instanced rendering
- **Complete COMPAS Integration**: Full support for all COMPAS objects based on the [compas.scene](https://compas.dev/compas/latest/api/generated/compas.scene.Scene.html#scene) architecture
- **Multiple Rendering Modes**: Shaded, ghosted, lighted, and wireframe rendering with configurable opacity
- **Interactive Navigation**: Smooth camera controls with perspective, orthographic, and preset views (top, front, right)
- **Advanced Selection**: Object selection with window/box selection, multi-selection, and selection highlighting

### User Interface
- **Customizable UI**: Fully configurable interface with dockable panels, toolbars, and sidebars
- **Scene Management**: Hierarchical scene tree with show/hide controls and object settings
- **Real-time Controls**: Dynamic sliders, buttons, and form controls for interactive parameter adjustment
- **Property Editing**: Built-in object property dialogs for colors, line widths, point sizes, and transformations

### Supported Geometry Types
- **Primitives**: Point, Line, Vector, Plane, Frame
- **Curves**: Polyline, Circle, Ellipse, NurbsCurve
- **Surfaces**: Polygon, NurbsSurface, BRep (via compas_occ)
- **Solids**: Box, Sphere, Cylinder, Cone, Torus, Capsule, Polyhedron
- **Data Structures**: Mesh, Graph, Pointcloud, Collection
- **Special**: Text tags, Grid, Custom buffer objects

### Advanced Features
- **Dynamic Animations**: Built-in animation system with `@viewer.on()` decorator for time-based updates
- **Multi-Unit Support**: Automatic scaling for meters, centimeters, and millimeters
- **Command System**: Extensive keyboard and mouse shortcuts with customizable bindings
- **File I/O**: Load/save scenes in JSON format, drag and drop COMPAS scene, geometries and data structures
- **Command Line Interface**: Direct launching with `python -m compas_viewer -f filename.json`
- **Extensible Architecture**: Plugin system for custom scene objects and UI components

## Installation

### Requirements
- Python >= 3.9
- COMPAS >= 2.2.0

### Quick Install
```bash
pip install compas_viewer
```

### Development Install
```bash
git clone https://github.com/compas-dev/compas_viewer.git
cd compas_viewer
pip install -e .
```

See the [Getting Started](https://compas.dev/compas_viewer/latest/installation.html) instructions in the docs for detailed installation guidelines.

## Quick Start

### Basic Usage
```python
from compas_viewer import Viewer
from compas.geometry import Box, Sphere

# Create viewer
viewer = Viewer()

# Add geometry
box = Box(1, 2, 3)
sphere = Sphere(0.5)

viewer.scene.add(box, name="My Box")
viewer.scene.add(sphere, name="My Sphere")

# Show viewer
viewer.show()
```

### Command Line Usage
```bash
# Launch with a empty scene
python -m compas_viewer

# Launch with a specific file
python -m compas_viewer -f path/to/geometry.json

# Launch with multiple files from a directory
python -m compas_viewer --files path/to/directory/
```

### Dynamic Animations
```python
from compas_viewer import Viewer
from compas.geometry import Box, Translation

viewer = Viewer()
box = viewer.scene.add(Box(1, 1, 1))

@viewer.on(interval=50)  # Update every 50ms
def animate(frame):
    T = Translation.from_vector([0.01 * frame, 0, 0])
    box.transformation = T

viewer.show()
```

## Key Controls

| Action | Shortcut |
|--------|----------|
| Rotate | Right-click + drag |
| Pan | Right-click + shift + drag |
| Zoom | Mouse wheel |
| Select object | Left-click |
| Select multiple | Left-click + shift + drag |
| Delete selected | Delete key |
| Zoom to selected | F key (with selection) |
| Zoom to All | F key (without selection) |

## Documentation

- **[Tutorial](https://compas.dev/compas_viewer/latest/tutorial.html)**: Basic concepts, configuration, and software architecture
- **[Examples](https://compas.dev/compas_viewer/latest/examples.html)**: Comprehensive examples covering all features
- **[API Reference](https://compas.dev/compas_viewer/latest/api.html)**: Complete API documentation

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for:
- Bug reports and feature requests
- Code contributions and pull requests
- Documentation improvements
- Community guidelines

## Dependencies

- **[PySide6](https://pypi.org/project/PySide6/)**: Qt6 bindings for Python
- **[PyOpenGL](https://pypi.org/project/PyOpenGL/)**: OpenGL bindings for Python
- **[freetype-py](https://pypi.org/project/freetype-py/)**: Font rendering
- **[COMPAS](https://compas.dev/)**: COMPAS framework (>= 2.2.0)

## License

The code in this repo is licensed under the [MIT License](LICENSE).

## Known Issues

Please check the [Issue Tracker](https://github.com/compas-dev/compas_viewer/issues) for known issues and their solutions.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.
