from compas.data import Data


class ViewerConfig(Data):
    """
    The class representation for the `viewer.json`.
    The viewer.json contains all the settings about the viewer application it self: with, height, full_screen, ...

    """

    DATASCHEMA = {
        "type": "object",
        "description": "description",
        "properties": {
            "about": {"type": "string", "description": "description"},
            "title": {"type": "string", "description": "description"},
            "width": {"type": "number", "description": "description"},
            "height": {"type": "number", "description": "description"},
            "full_screen": {"type": "boolean", "description": "description"},
        },
    }

    def __init__(self, about: str, title: str, width: int, height: int, full_screen: bool) -> None:
        super(ViewerConfig, self).__init__()
        self.about = about
        self.title = title
        self.width = width
        self.height = height
        self.full_screen = full_screen

    @property
    def data(self):  # -> dict[str, Any]:
        return {"about": self.about, "title": self.title, "width": self.width, "height": self.height, "full_screen": self.full_screen}

    @classmethod
    def from_data(cls, data):
        return cls(about=data["about"], title=data["title"], width=data["width"], height=data["height"], full_screen=data["full_screen"])
