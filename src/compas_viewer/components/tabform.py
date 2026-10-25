from typing import Literal

from PySide6.QtWidgets import QTabWidget

from .component import Component
from .container import Container


class Tabform(Component):
    """
    A component to create a tabbed interface using QTabWidget.

    This component follows the same pattern as ObjectSetting but provides
    a tabbed interface where each tab can contain different content.

    Parameters
    ----------
    tab_position
        Position of the tabs. Options are "top", "bottom", "left", "right".
        Defaults to "top".

    Examples
    --------
    >>> tabform = Tabform()
    >>> tabform.add_tab("Settings", container_type="scrollable")
    >>> tabform.add_tab("Options", container_type="standard")
    >>> tabform.populate_tab("Settings", some_components)

    """

    def __init__(self, tab_position: str = "top") -> None:
        super().__init__()

        self.widget = QTabWidget()
        self.tabs: dict[str, Container] = {}

        # Set tab position
        position_map = {"top": QTabWidget.North, "bottom": QTabWidget.South, "left": QTabWidget.West, "right": QTabWidget.East}
        self.widget.setTabPosition(position_map.get(tab_position, QTabWidget.North))

        # Connect tab change signal
        self.widget.currentChanged.connect(self.on_tab_changed)

    def add_tab(
        self,
        name: str,
        container: Container | None = None,
        container_type: Literal["standard", "scrollable", "splitter"] = "standard",
    ) -> Container:
        """
        Add a new tab with the given name and container.

        Parameters
        ----------
        name
            The name/title of the tab.
        container
            The container to use for this tab. If None, a new container will be created.
        container_type
            Type of container for the tab if container is None. Options are "standard", "scrollable", "splitter".
            Defaults to "standard".

        Returns
        -------
        Container
            The container that was added to this tab.

        """
        if name in self.tabs:
            raise ValueError(f"Tab '{name}' already exists")

        # Use provided container or create a new one
        if container is None:
            container = Container(container_type=container_type)

        self.tabs[name] = container

        # Add the tab to the widget
        self.widget.addTab(container.widget, name)

        return container

    def remove_tab(self, name: str) -> None:
        """
        Remove a tab by name.

        Parameters
        ----------
        name
            The name of the tab to remove.

        """
        if name not in self.tabs:
            raise ValueError(f"Tab '{name}' does not exist")

        # Find the index of the tab
        for i in range(self.widget.count()):
            if self.widget.tabText(i) == name:
                self.widget.removeTab(i)
                break

        # Remove from our tracking dictionary
        del self.tabs[name]

    def get_tab(self, name: str) -> Container | None:
        """
        Get the container for a specific tab.

        Parameters
        ----------
        name
            The name of the tab.

        Returns
        -------
        Container | None
            The container for the tab, or None if not found.

        """
        return self.tabs.get(name)

    def populate_tab(self, tab_name: str, components: list[Component]) -> None:
        """
        Populate a tab with components.

        Parameters
        ----------
        tab_name
            The name of the tab to populate.
        components
            List of components to add to the tab.

        """
        if tab_name not in self.tabs:
            raise ValueError(f"Tab '{tab_name}' does not exist")

        container = self.tabs[tab_name]
        container.reset()

        for component in components:
            container.add(component)

    def set_current_tab(self, name: str) -> None:
        """
        Set the current active tab by name.

        Parameters
        ----------
        name
            The name of the tab to make active.

        """
        if name not in self.tabs:
            raise ValueError(f"Tab '{name}' does not exist")

        for i in range(self.widget.count()):
            if self.widget.tabText(i) == name:
                self.widget.setCurrentIndex(i)
                break

    def get_current_tab_name(self) -> str | None:
        """
        Get the name of the currently active tab.

        Returns
        -------
        str | None
            The name of the current tab, or None if no tabs exist.

        """
        current_index = self.widget.currentIndex()
        if current_index >= 0:
            return self.widget.tabText(current_index)
        return None

    def on_tab_changed(self, index: int) -> None:
        """
        Handle tab change events.

        Parameters
        ----------
        index
            The index of the newly selected tab.

        """
        # This can be overridden by subclasses to handle tab changes
        pass

    def update(self) -> None:
        """Update all tabs and their contents."""
        super().update()
        for container in self.tabs.values():
            container.update()

    def reset(self) -> None:
        """Reset all tabs by removing all tabs and clearing the tabs dictionary."""
        # Remove all tabs
        while self.widget.count() > 0:
            self.widget.removeTab(0)

        # Clear the tabs dictionary
        self.tabs.clear()

    def display_text(self, text: str, tab_name: str = "Info") -> None:
        """
        Display text in a tab. If the tab doesn't exist, create it.

        Parameters
        ----------
        text
            The text to display.
        tab_name
            The name of the tab to display the text in. Defaults to "Info".

        """
        if tab_name not in self.tabs:
            self.add_tab(tab_name, container_type="standard")

        container = self.tabs[tab_name]
        container.display_text(text)
