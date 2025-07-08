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
            # Create the instance without calling __init__
            instance = cls.__new__(cls)
            # Store it immediately so it's available during __init__
            cls._instances[key_class] = instance
            # Now call __init__ on the stored instance
            instance.__init__(*args, **kwargs)
        return cls._instances[key_class]


class Singleton(metaclass=SingletonMeta):
    """Singleton base class."""
