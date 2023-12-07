from compas.data import Data


class ComponentConfig(Data):
    """
    The class representation of a single component: render, plot, menu, ...
    """

    def __init__(self, component_config: dict) -> None:
        for key, value in component_config.items():
            setattr(self, key, value)

    @property
    def data(self):  # -> dict[str, Any]:
        return {"type": self.type, "name": self.name, "settings": self.settings}

    @classmethod
    def from_data(cls, data):
        return cls(type=data["type"], name=data["name"], settings=data["settings"])




class ComponentsConfig(Data):
    """
    The class representation for the `components.json`.
    The `components.json` contains all the settings about each component:
    For renders : background color, grid, ...
    """

    def __init__(self, component_config: dict) -> None:
        for key, value in component_config.items():
            setattr(self, key, value)

    @property
    def data(self):  # -> dict[str, Any]:
        return {"about": self.about, "title": self.title, "width": self.width, "height": self.height, "full_screen": self.full_screen}

    @classmethod
    def from_data(cls, data):
        return cls(about=data["about"], title=data["title"], width=data["width"], height=data["height"], full_screen=data["full_screen"])
