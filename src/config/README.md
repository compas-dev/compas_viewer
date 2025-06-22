# Configuration Structure

This directory contains the new Pydantic-based configuration system for COMPAS Viewer.

## Key Features

- **Serializable**: All configuration classes can be saved/loaded as JSON
- **Type-safe**: Full type hints and validation using Pydantic
- **Clean separation**: UI definitions with lambdas are separate from config data
- **Modular**: Each domain has its own configuration module
- **Native Pydantic**: Uses Pydantic's built-in methods directly (no wrapper classes)

## Structure

```
config/
├── __init__.py          # Exports main Config class
├── window.py           # Window configuration
├── renderer.py         # Renderer, display, camera, and view3d configs
├── ui.py               # UI layout settings (show/hide flags only)
├── main.py             # Main Config class combining all others
├── ui_definitions.py   # UI structures with lambdas (non-serializable)
├── example.py          # Usage examples
├── README.md           # This file
└── MIGRATION.md        # Migration guide
```

## Usage

### Basic Usage

```python
from config import Config

# Create with defaults
config = Config()

# Load from JSON file (convenience method)
config = Config.from_json_file("settings.json")

# Save to JSON file (convenience method)
config.to_json_file("settings.json")

# Update values
config.window.width = 1920
config.ui.sidebar.show = False
```

### Native Pydantic Methods

```python
# Create from dictionary
config = Config.model_validate(data_dict)

# Create from JSON string
config = Config.model_validate_json(json_string)

# Convert to dictionary
data = config.model_dump()

# Convert to JSON string
json_str = config.model_dump_json(indent=2)

# Copy with updates
new_config = config.model_copy(update={"vectorsize": 0.2})
```

### Accessing Configuration

```python
# Window settings
config.window.title = "My Viewer"
config.window.width = 1920
config.window.height = 1080

# UI visibility
config.ui.toolbar.show = True
config.ui.sidebar.show = False

# Renderer settings
config.renderer.rendermode = "wireframe"
config.renderer.backgroundcolor = "#f0f0f0"

# Camera settings
config.camera.fov = 60.0
config.camera.position = [0, 0, 10]
```

## Why No BaseConfig?

We initially considered a BaseConfig wrapper class, but **Pydantic already provides everything we need**:

| **Custom Method** | **Native Pydantic** | **Why Native is Better** |
|------------------|---------------------|--------------------------|
| `from_dict(data)` | `Config.model_validate(data)` | More explicit, standard |
| `to_dict()` | `config.model_dump()` | Standard method name |
| `from_json(path)` | `Config.model_validate_json(json_str)` | Works with strings |
| `to_json(path)` | `config.model_dump_json()` | Works with strings |
| `update(**kwargs)` | `config.model_copy(update=kwargs)` | Immutable, safer |

**Only added convenience**: File I/O methods (`from_json_file`/`to_json_file`) for working with file paths instead of strings.

## Migration from Old Config

The old dataclass-based config has been replaced with this Pydantic structure:

### What Changed

1. **Color objects → Hex strings**: `Color.black()` → `"#000000"`
2. **Lambda functions removed**: Moved to `ui_definitions.py`
3. **Nested structure simplified**: Cleaner hierarchy
4. **Type validation**: Automatic validation of all values
5. **Native Pydantic**: Uses standard Pydantic methods

### Migration Steps

1. Replace `from compas_viewer.config import Config` with `from config import Config`
2. Update color assignments to use hex strings
3. Use `ui_definitions.py` functions for UI structure instead of config
4. Use native Pydantic methods instead of custom wrapper methods

## UI Definitions

The complex UI structures with lambdas and function references are now in `ui_definitions.py`:

```python
from config.ui_definitions import (
    get_default_menu_items,
    get_default_sidebar_items,
    get_default_camera_dialog_settings,
    get_default_commands
)

# Use in UI builders
menu_items = get_default_menu_items()
sidebar_items = get_default_sidebar_items()
```

## Benefits

1. **Serializable**: Can save/load complete configuration as JSON
2. **Type Safety**: Pydantic validates all types and values
3. **Clean**: No more mixing of data and UI definitions
4. **Standard**: Uses Pydantic's standard methods
5. **Maintainable**: Clear separation of concerns
6. **Extensible**: Easy to add new configuration options

## Example JSON Output

```json
{
  "vectorsize": 0.1,
  "unit": "m",
  "window": {
    "title": "COMPAS Viewer",
    "width": 1280,
    "height": 720,
    "fullscreen": false,
    "about": "Stand-alone viewer for COMPAS."
  },
  "ui": {
    "toolbar": {"show": false},
    "sidebar": {"show": true, "sceneform_visible": true},
    "statusbar": {"show": true}
  },
  "renderer": {
    "rendermode": "shaded",
    "backgroundcolor": "#ffffff",
    "show_grid": true
  },
  "camera": {
    "fov": 45.0,
    "position": [-10.0, -10.0, 10.0],
    "target": [0.0, 0.0, 0.0]
  }
}
``` 