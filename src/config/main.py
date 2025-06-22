import json
from pathlib import Path
from typing import Literal, Union

from .base import BaseConfig
from .window import WindowConfig
from .renderer import RendererConfig, CameraConfig
from .ui import UIConfig


class Config(BaseConfig):
    """Main configuration class for the COMPAS Viewer."""
    
    # Basic settings
    vectorsize: float = 0.1
    unit: Literal["m", "cm", "mm"] = "m"
    
    # Component configurations
    window: WindowConfig = WindowConfig()
    ui: UIConfig = UIConfig()
    renderer: RendererConfig = RendererConfig()
    camera: CameraConfig = CameraConfig()
    
    # Convenience methods for file I/O (only useful additions over Pydantic)
    @classmethod
    def from_json_file(cls, filepath: Union[str, Path]) -> 'Config':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            return cls.model_validate_json(f.read())
    
    def to_json_file(self, filepath: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            f.write(self.model_dump_json(indent=2)) 