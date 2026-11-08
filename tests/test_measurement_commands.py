from unittest.mock import Mock
from unittest.mock import call

from compas_viewer.commands import add_associative_distance_dimension
from compas_viewer.commands import add_fixed_distance_dimension
from compas_viewer.commands import builtin_commands
from compas_viewer.commands import cancel_measurement
from compas_viewer.commands import inspect_distance
from compas_viewer.uidefinitions import default_menu_items


def test_measurement_commands_delegate_to_viewer_facade():
    viewer = Mock()
    viewer.cancel_measurement.return_value = True

    inspect_distance(viewer)
    add_fixed_distance_dimension(viewer)
    add_associative_distance_dimension(viewer)
    canceled = cancel_measurement(viewer)

    viewer.start_distance_inspection.assert_called_once_with()
    assert viewer.start_distance_dimension.call_args_list == [call("fixed"), call("associative")]
    viewer.cancel_measurement.assert_called_once_with()
    assert canceled


def test_measurement_commands_have_stable_registry_identifiers():
    commands = builtin_commands()

    assert commands["viewer.inspect_distance"].callback is inspect_distance
    assert commands["viewer.add_fixed_distance_dimension"].callback is add_fixed_distance_dimension
    assert commands["viewer.add_associative_distance_dimension"].callback is add_associative_distance_dimension
    assert commands["viewer.cancel_measurement"].callback is cancel_measurement


def test_measure_menu_uses_measurement_commands():
    menu = next(item for item in default_menu_items() if item.get("title") == "Measure")

    assert menu.get("items") == [
        {"title": "Inspect Distance", "command": "viewer.inspect_distance"},
        {"type": "separator"},
        {"title": "Add Fixed Distance Dimension", "command": "viewer.add_fixed_distance_dimension"},
        {"title": "Add Associative Distance Dimension", "command": "viewer.add_associative_distance_dimension"},
        {"type": "separator"},
        {"title": "Cancel Measurement", "command": "viewer.cancel_measurement"},
    ]
