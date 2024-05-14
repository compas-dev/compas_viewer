from PySide6 import QtWidgets

from .setting_components import SettingComponents
from .treeform_components import TreeformComponents


class ComponentsManager:
    """
    The ComponentsManager class is designed to manage and integrate various UI components
    from different component groups within a single manager. This enables efficient
    aggregation and control of widgets from separate component classes, facilitating
    easier management of complex GUI structures.

    This class combines widgets from setting components and treeform components or more,
    allowing them to be added dynamically to any specified parent widget within a Qt application.

    Attributes
    ----------
    setting_components : :class:`SettingComponents`
        An instance of SettingComponents which manages individual setting-related widgets.
    treeform_components : :class:`TreeformComponents`
        An instance of TreeformComponents which manages tree structure-related widgets.
    all_widgets : dict
        A dictionary containing all widgets from all components.
    manager_widgets : dict
        A dictionary to store widgets that are actively managed and displayed in the UI.

    Methods
    -------
    add_widgets(widget_keys: list[str])
        Adds widgets to the manager's active list based on the provided widget keys. If a key is not
        found, it prints an error message.
    setup_widgets(parent_widget: :class:`QtWidgets.QWidget`)
        Adds all managed widgets to the specified parent widget, ensuring they are displayed in the GUI.

    Raises
    ------
    TypeError
        If the provided parent_widget is not an instance of :class:`QtWidgets.QWidget`.

    See Also
    --------
    :class:`SettingComponents`
    :class:`TreeformComponents`

    Examples
    --------
    >>> manager = ComponentsManager()  # doctest: +SKIP
    >>> manager.add_widgets(["setting1", "treeform1"])  # doctest: +SKIP
    >>> parent_widget = QtWidgets.QWidget()  # doctest: +SKIP
    >>> manager.setup_widgets(parent_widget)  # doctest: +SKIP

    """

    def __init__(self):
        self.setting_components = SettingComponents()
        self.treeform_components = TreeformComponents()
        self.all_widgets: dict = None
        self.manager_widgets = {}

    def lazy_init(self):
        self.setting_components.lazy_init()
        self.treeform_components.lazy_init()
        self.all_widgets = {**self.setting_components.widgets, **self.treeform_components.widgets}

    def add_widgets(self, widget_keys: list[str]):
        for key in widget_keys:
            widget_instance = self.all_widgets.get(key)
            if widget_instance:
                self.manager_widgets[key] = widget_instance
            else:
                print(f"Components manager failed to locate widget of type {key}")

    def setup_widgets(self, parent_widget: QtWidgets.QWidget):
        if not isinstance(parent_widget, QtWidgets.QWidget):
            raise TypeError("parent_widget must be a QtWidgets.QWidget")
        for widget in self.manager_widgets.values():
            parent_widget.addWidget(widget)
        return parent_widget
