from typing import Any
from typing import cast


class SingletonMeta(type):
    """Cache one instance for each direct subclass of `Singleton`."""

    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        # Check if this class is a direct subclass of Singleton
        key_class: type = cls
        base_class = key_class.__base__
        while base_class is not Singleton and base_class is not None:
            key_class = base_class
            base_class = key_class.__base__

        if key_class not in cls._instances:
            instance = cast(Any, cls.__new__)(cls)
            cls._instances[key_class] = instance
            instance.__init__(*args, **kwargs)
        return cls._instances[key_class]


class Singleton(metaclass=SingletonMeta):
    """Base class for objects that have one shared instance per class family."""
