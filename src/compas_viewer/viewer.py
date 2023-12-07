from abc import ABC


class Viewer(ABC):
    """
    The Viewer class is the main entry for launching the viewer application.

    Parameters
    ----------
    configuration : str, optional
        The path to the `.viewer` file, or the the path to the folder which contains the configuration files. incomplete contents would be filled with default configuration values.

    Attributes
    ----------
    width : int
        The width of the app window at startup.
    height : int
        The height of the app window at startup.
    full_screen : bool
        Whether the app window is full_screen at startup. If True, the width and height are ignored.
    view_mode : {'shaded', 'ghosted', 'wire_frame', 'lighted'}
        The display mode of the OpenGL view. In `ghosted` mode, all objects have a default opacity of 0.7.
    show_grid : bool
        Show the XY plane.
    """

    def __init__(self, configuration=None) -> None:
        pass
