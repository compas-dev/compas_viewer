#!/usr/bin/env python3
"""
Example usage of the new Pydantic-based configuration system.
Shows native Pydantic methods vs custom wrapper methods.
"""

from main import Config
from ui_definitions import get_default_menu_items, get_default_sidebar_items


def main():
    """Demonstrate the new configuration system."""
    
    print("=== COMPAS Viewer - New Configuration System ===\n")
    
    # Create default configuration
    config = Config()
    
    print("1. Default Configuration:")
    print(f"   Window: {config.window.width}x{config.window.height}")
    print(f"   Render mode: {config.renderer.rendermode}")
    print(f"   Background: {config.renderer.backgroundcolor}")
    print(f"   Sidebar visible: {config.ui.sidebar.show}")
    
    # Modify configuration
    print("\n2. Modifying Configuration:")
    config.window.width = 1920
    config.window.height = 1080
    config.window.title = "My Custom Viewer"
    config.renderer.rendermode = "wireframe"
    config.renderer.backgroundcolor = "#f0f0f0"
    config.ui.sidebar.show = False
    
    print(f"   New window size: {config.window.width}x{config.window.height}")
    print(f"   New title: {config.window.title}")
    print(f"   New render mode: {config.renderer.rendermode}")
    print(f"   New background: {config.renderer.backgroundcolor}")
    print(f"   Sidebar hidden: {not config.ui.sidebar.show}")
    
    # Save/load configuration using Pydantic methods
    print("\n3. Using Native Pydantic Methods:")
    
    # To JSON string
    json_str = config.model_dump_json(indent=2)
    print(f"   JSON string length: {len(json_str)} characters")
    
    # From JSON string  
    loaded_from_json = Config.model_validate_json(json_str)
    print(f"   Loaded from JSON: {loaded_from_json.window.title}")
    
    # To dict
    config_dict = config.model_dump()
    print(f"   Dict keys: {list(config_dict.keys())}")
    
    # From dict
    loaded_from_dict = Config.model_validate(config_dict)
    print(f"   Loaded from dict: {loaded_from_dict.renderer.rendermode}")
    
    # Update with model_copy
    updated_config = config.model_copy(update={"vectorsize": 0.2})
    print(f"   Updated vectorsize: {updated_config.vectorsize}")
    
    # File I/O with convenience methods (only added value over Pydantic)
    print("\n4. File I/O Convenience Methods:")
    config.to_json_file("example_config.json")
    print("   Saved to 'example_config.json' using convenience method")
    
    loaded_config = Config.from_json_file("example_config.json")
    print(f"   Loaded from file: {loaded_config.window.width}x{loaded_config.window.height}")
    
    # Demonstrate UI definitions (separate from config)
    print("\n5. UI Definitions (separate from config):")
    menu_items = get_default_menu_items()
    sidebar_items = get_default_sidebar_items()
    
    print(f"   Menu sections: {len(menu_items)}")
    print(f"   Menu titles: {[item['title'] for item in menu_items]}")
    print(f"   Sidebar panels: {len(sidebar_items)}")
    print(f"   Sidebar types: {[item['type'] for item in sidebar_items]}")
    
    # Demonstrate type validation
    print("\n6. Type Validation:")
    try:
        config.window.width = "invalid"  # This should fail
    except Exception as e:
        print(f"   ✓ Validation caught invalid width: {type(e).__name__}")
    
    try:
        config.renderer.rendermode = "invalid_mode"  # This should fail
    except Exception as e:
        print(f"   ✓ Validation caught invalid render mode: {type(e).__name__}")
    
    print("\n=== Why BaseConfig wasn't needed ===")
    print("   Pydantic already provides:")
    print("   • model_validate() - create from dict")
    print("   • model_validate_json() - create from JSON string")
    print("   • model_dump() - convert to dict")
    print("   • model_dump_json() - convert to JSON string")
    print("   • model_copy(update=...) - copy with updates")
    print("   • Automatic type validation")
    print("   • Direct attribute assignment")
    
    print("\n=== Configuration System Demo Complete ===")


if __name__ == "__main__":
    main() 