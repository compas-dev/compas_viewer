from typing import TypedDict
from typing import Union

from compas.data import Data


class Config(Data):
    """
    The abstract class for different configurations.
    """

    def __init__(self, config: Union[TypedDict, dict]):
        super(Config, self).__init__()
        self.config = config

    @property
    def data(self):  # -> dict[str, Any]:
        return self.config

    @classmethod
    def from_data(cls, data):
        return cls(config=data)
