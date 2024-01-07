from collections import defaultdict
from typing import Any, Callable, Dict


ITEM_LAYOUTS: Dict[str, Callable] = defaultdict()


def register(name: str, layout_class: Callable):
    """Register an layout class with its name.

    Parameters
    ----------
    name : str
        The name of the layout.
    layout_class : Callable
        The layout class.

    """
    ITEM_LAYOUTS[name] = layout_class


def register_layouts():
    register("menu", Menu)
    register("layout", Layout)
    


def get_layout_cls(name: str) -> Any:
    cls = ITEM_LAYOUTS.get(name)

    if cls is None:
        raise ValueError(f"Layout {name} not found. Check the name and the registration.")
    return cls


# Putting imports here to avoid circular imports
from .layout import Layout  # noqa: F401
from .menu import Menu  # noqa: F401

register_layouts()

___all__ = [
    "layout",
    "basic_layout",
    "Layout",
    "BasicLayout",
]
