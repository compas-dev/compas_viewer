from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Geometry


class Collection(Data):
    def __init__(self, items: list[Geometry | Mesh] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.items = items or []

    @property
    def __data__(self) -> dict[str, list[Geometry | Mesh]]:
        return {"items": self.items}
