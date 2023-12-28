from collections import defaultdict
from typing import Any, Callable, Dict


ITEM_ACTIONS: Dict[str, Callable] = defaultdict()


def register(name: str, action_class: Callable):
    """Register an action class with its name.

    Parameters
    ----------
    name : str
        Name of the action.
    action_class : :class:`Action`
        Action class.

    Returns
    -------
    None

    """
    ITEM_ACTIONS[name] = action_class


def register_actions():
    register("zoom_selected", ZoomSelected)
    register("print_gl_info", GLInfo)


def get_action_cls(name: str) -> Any:
    cls = ITEM_ACTIONS.get(name)

    if cls is None:
        raise ValueError(f"Action {name} not found. Check the name and the registration.")
    return cls


# Putting imports here to avoid circular imports
from .action import Action  # noqa: F401 E402
from .zoom_selected import ZoomSelected  # noqa: E402
from .print_gl_info import GLInfo  # noqa: E402

register_actions()

___all__ = [
    "Action",
    "ZoomSelected",
]
