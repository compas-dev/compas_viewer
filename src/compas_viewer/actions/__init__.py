from collections import defaultdict
from typing import Any, Callable


ITEM_ACTIONS: dict[str, Callable] = defaultdict()


def register(name: str, action_class: Callable):
    """Register an action class with its name.

    Parameters
    ----------
    name : str
        Name of the action.
    action_class : :class:`Action`
        Action class.

    """
    ITEM_ACTIONS[name] = action_class


def register_actions():
    register("zoom_selected", ZoomSelected)
    register("print_gl_info", GLInfo)
    register("select_all", SelectAll)
    register("view_right", ViewRight)
    register("view_front", ViewFront)
    register("view_top", ViewTop)
    register("view_perspective", ViewPerspective)
    register("delete_selected", DeleteSelected)


def get_action_cls(name: str) -> Any:
    cls = ITEM_ACTIONS.get(name)

    if cls is None:
        raise ValueError(f"Action {name} not found. Check the name and the registration.")
    return cls


# Putting imports here to avoid circular imports
from .action import Action  # noqa: F401 E402
from .zoom_selected import ZoomSelected  # noqa: E402
from .print_gl_info import GLInfo  # noqa: E402
from .select_all import SelectAll  # noqa: E402
from .viewmode import ViewRight, ViewFront, ViewTop, ViewPerspective  # noqa: E402
from .delete_selected import DeleteSelected  # noqa: E402

register_actions()

___all__ = [
    "Action",
    "ZoomSelected",
    "GLInfo",
    "SelectAll",
    "ViewRight",
    "ViewFront",
    "ViewTop",
    "ViewPerspective",
    "DeleteSelected",
]
