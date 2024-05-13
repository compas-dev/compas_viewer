class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Check if this class is a direct subclass of Singleton
        if cls.__base__ is Singleton:
            key_class = cls
        else:
            # Walk up the chain to find the first subclass of Singleton
            key_class = cls
            while key_class.__base__ is not Singleton:
                key_class = key_class.__base__

        if key_class not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key_class] = instance
        return cls._instances[key_class]


class Singleton(metaclass=SingletonMeta):
    """Singleton base class."""
