from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    """Base configuration class with shared model configuration."""
    
    model_config = ConfigDict(
        extra='forbid',
        validate_assignment=True,
    ) 