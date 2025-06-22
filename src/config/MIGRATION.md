# Migration Guide: Dataclass to Pydantic Configuration

This guide helps you migrate from the old dataclass-based configuration system to the new Pydantic-based system.

## Key Changes

### 1. Import Changes

**Old:**
```python
from compas_viewer.config import Config
```

**New:**
```python
from config import Config
```

### 2. Color Handling

**Old:**
```python
from compas.colors import Color

config.renderer.backgroundcolor = Color.white()
config.display.pointcolor = Color.black()  
```

**New:**
```python
config.renderer.backgroundcolor = "#ffffff"
config.display.pointcolor = "#000000"
```

### 3. Configuration Methods

**Old:** Custom wrapper methods
```python
config = Config.from_json("settings.json")
config.to_json("settings.json")
data = config.to_dict()
```

**New:** Native Pydantic methods (preferred)
```python
# File I/O (convenience methods)
config = Config.from_json_file("settings.json")
config.to_json_file("settings.json")

# Standard Pydantic methods
config = Config.model_validate_json(json_string)
json_str = config.model_dump_json(indent=2)
data = config.model_dump()
new_config = config.model_copy(update={"vectorsize": 0.2})
```

### 4. UI Definitions

**Old:** UI structure was embedded in config classes with lambdas
```python
# This was inside MenubarConfig
_items = [
    {
        "title": "View",
        "items": [
            {"title": toggle_toolbar_cmd.title, 
             "action": toggle_toolbar_cmd,
             "checked": lambda viewer: viewer.config.ui.toolbar.show}
        ]
    }
]
```

**New:** UI definitions are separate from configuration
```python
from config.ui_definitions import get_default_menu_items

# In your UI builder
menu_items = get_default_menu_items()
```

### 5. Configuration Access

**Old:**
```python
# Dataclass field access
config.ui.menubar.items  # This contained lambdas
config.ui.sidebar.items  # This contained lambdas
```

**New:**
```python
# Simple settings only
config.ui.menubar.show  # bool
config.ui.sidebar.show  # bool
config.ui.sidebar.sceneform_visible  # bool

# UI structure from separate module
from config.ui_definitions import get_default_sidebar_items
sidebar_items = get_default_sidebar_items()
```

## Step-by-Step Migration

### Step 1: Update Dependencies

Add to your `requirements.txt`:
```
pydantic >= 2.0.0
```

### Step 2: Update Imports

Replace all instances of:
```python
from compas_viewer.config import Config
```

with:
```python
from config import Config
```

### Step 3: Update Color Usage

Find and replace color objects with hex strings:

```python
# Old patterns
Color.white() → "#ffffff"
Color.black() → "#000000"  
Color.red() → "#ff0000"
Color.green() → "#00ff00"
Color.blue() → "#0000ff"
Color.grey() → "#808080"
Color(0.7, 0.7, 0.7) → "#b3b3b3"
Color(1.0, 1.0, 0.0, 1.0) → "#ffff00"
```

### Step 4: Update Configuration Methods

Replace custom wrapper methods with native Pydantic:

```python
# Old wrapper methods → New native Pydantic
config.from_json(path) → Config.from_json_file(path)  # convenience
config.to_json(path) → config.to_json_file(path)      # convenience
config.from_dict(data) → Config.model_validate(data)
config.to_dict() → config.model_dump()
config.update(**kwargs) → config.model_copy(update=kwargs)

# Additional native methods
Config.model_validate_json(json_str)  # from JSON string
config.model_dump_json(indent=2)      # to JSON string
```

### Step 5: Update UI Builders

Replace direct config access for UI structure:

**Old:**
```python
class MenuBar:
    def __init__(self, ui, items):
        self.items = items  # This came from config
        # build menu from self.items
```

**New:**
```python
from config.ui_definitions import get_default_menu_items

class MenuBar:
    def __init__(self, ui):
        self.items = get_default_menu_items()
        # build menu from self.items
```

### Step 6: Update Configuration Creation

**Old:**
```python
# Complex nested initialization
config = Config(
    ui=UIConfig(
        menubar=MenubarConfig(items=complex_menu_structure),
        sidebar=SidebarConfig(items=complex_sidebar_structure)
    )
)
```

**New:**
```python
# Simple initialization
config = Config()
# or
config = Config(
    window=WindowConfig(width=1920, height=1080),
    ui=UIConfig(sidebar=SidebarConfig(show=False))
)
```

## Common Migration Issues

### Issue 1: Lambda Functions in Config

**Error:** `TypeError: Object of type function is not JSON serializable`

**Solution:** Move lambda functions to `ui_definitions.py`

### Issue 2: Color Object Assignment

**Error:** `ValidationError: Input should be a valid string`

**Solution:** Replace Color objects with hex strings

### Issue 3: Missing UI Structure

**Error:** `AttributeError: 'MenubarConfig' object has no attribute 'items'`

**Solution:** Use `ui_definitions` functions instead of config items

### Issue 4: Custom Method Not Found

**Error:** `AttributeError: 'Config' object has no attribute 'to_dict'`

**Solution:** Use native Pydantic methods:
- `config.to_dict()` → `config.model_dump()`
- `Config.from_dict(data)` → `Config.model_validate(data)`
- `config.update(**kwargs)` → `config.model_copy(update=kwargs)`

## Native Pydantic Benefits

| **Aspect** | **Old Custom Methods** | **Native Pydantic** |
|------------|----------------------|-------------------|
| **JSON** | `to_json()`, `from_json()` | `model_dump_json()`, `model_validate_json()` |
| **Dict** | `to_dict()`, `from_dict()` | `model_dump()`, `model_validate()` |
| **Update** | `update(**kwargs)` | `model_copy(update=kwargs)` |
| **Standards** | Custom naming | Standard Pydantic API |
| **Immutability** | Mutates object | Returns new instance |
| **Documentation** | Custom docs | Official Pydantic docs |

## Benefits After Migration

1. **JSON Serialization**: Full config can be saved/loaded
2. **Type Safety**: Automatic validation of all values
3. **Standard API**: Uses well-documented Pydantic methods
4. **Immutable Updates**: Safer configuration changes
5. **Cleaner Code**: Separation of data and UI definitions
6. **Better Testing**: Easier to test individual components
7. **Performance**: Faster config access and validation

## Validation

After migration, test that your configuration works:

```python
from config import Config

# Test basic functionality
config = Config()

# Test serialization with native methods
json_str = config.model_dump_json(indent=2)
loaded = Config.model_validate_json(json_str)

# Test file I/O with convenience methods
config.to_json_file("test_config.json")
loaded_file = Config.from_json_file("test_config.json")

# Test type validation
try:
    config.window.width = "invalid"
    assert False, "Should have raised ValidationError"
except ValidationError:
    print("✓ Type validation working")

# Test immutable updates
new_config = config.model_copy(update={"vectorsize": 0.2})
assert config.vectorsize != new_config.vectorsize
print("✓ Immutable updates working")
```

## Need Help?

- Check `config/example.py` for usage examples
- Read `config/README.md` for full documentation
- Review native Pydantic methods in the official docs
- Test individual components with the new system 