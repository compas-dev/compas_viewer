import numpy as np

from compas.typing import RealInput
from compas_viewer.renderer.camera import Position


def test_position_accepts_numpy_coordinates_and_normalizes_storage():
    values = np.array([1.0, 2.0, 3.0], dtype=np.float32)

    position = Position(values)

    assert all(type(coordinate) is float for coordinate in position)
    assert list(position) == list(values)


def test_position_setter_notifies_with_original_value_before_normalizing():
    updates: list[list[RealInput]] = []
    position = Position([0.0, 0.0, 0.0], on_update=lambda values: updates.append(list(values)))
    value = np.float32(1.5)

    position.x = value

    assert updates[-1][0] is value
    assert type(position.x) is float
    assert position.x == value


def test_position_set_notifies_with_original_values_before_normalizing():
    updates: list[list[RealInput]] = []
    position = Position([0.0, 0.0, 0.0], on_update=lambda values: updates.append(list(values)))
    values = [np.float32(1.0), np.float64(2.0), np.int32(3)]

    position.set(*values)

    assert all(actual is expected for actual, expected in zip(updates[-1], values))
    assert all(type(coordinate) is float for coordinate in position)
    assert list(position) == values
