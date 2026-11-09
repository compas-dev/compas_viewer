from unittest.mock import Mock
from unittest.mock import call

import pytest

from compas_viewer._scalar_measurement import ScalarMeasurementError
from compas_viewer.commands import add_associative_distance_dimension
from compas_viewer.commands import add_fixed_distance_dimension
from compas_viewer.commands import builtin_commands
from compas_viewer.commands import cancel_measurement
from compas_viewer.commands import inspect_distance
from compas_viewer.commands import inspect_selected_area
from compas_viewer.commands import inspect_selected_volume
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
    assert commands["viewer.inspect_selected_area"].callback is inspect_selected_area
    assert commands["viewer.inspect_selected_volume"].callback is inspect_selected_volume
    assert commands["viewer.add_fixed_distance_dimension"].callback is add_fixed_distance_dimension
    assert commands["viewer.add_associative_distance_dimension"].callback is add_associative_distance_dimension
    assert commands["viewer.cancel_measurement"].callback is cancel_measurement


def test_measure_menu_uses_measurement_commands():
    menu = next(item for item in default_menu_items() if item.get("title") == "Measure")

    assert menu.get("items") == [
        {"title": "Inspect Distance", "command": "viewer.inspect_distance"},
        {"title": "Inspect Selected Area", "command": "viewer.inspect_selected_area"},
        {"title": "Inspect Selected Volume", "command": "viewer.inspect_selected_volume"},
        {"type": "separator"},
        {"title": "Add Fixed Distance Dimension", "command": "viewer.add_fixed_distance_dimension"},
        {"title": "Add Associative Distance Dimension", "command": "viewer.add_associative_distance_dimension"},
        {"type": "separator"},
        {"title": "Cancel Measurement", "command": "viewer.cancel_measurement"},
    ]


def test_scalar_measurement_commands_format_declared_units(monkeypatch):
    information = Mock()
    monkeypatch.setattr("compas_viewer.commands.QMessageBox.information", information)
    viewer = Mock()
    viewer.ui.window.widget = parent = object()
    viewer.config.measurement.precision = 2
    viewer.config.measurement.unit = "m"
    viewer.inspect_selected_area.return_value = 12.345
    viewer.inspect_selected_volume.return_value = 6.789

    assert inspect_selected_area(viewer) == pytest.approx(12.345)
    assert inspect_selected_volume(viewer) == pytest.approx(6.789)
    assert information.call_args_list == [
        call(parent, "Selected Area", "Area: 12.35 m²"),
        call(parent, "Selected Volume", "Volume: 6.79 m³"),
    ]


def test_scalar_measurement_commands_report_expected_and_operation_failures(monkeypatch):
    information = Mock()
    critical = Mock()
    monkeypatch.setattr("compas_viewer.commands.QMessageBox.information", information)
    monkeypatch.setattr("compas_viewer.commands.QMessageBox.critical", critical)
    viewer = Mock()
    viewer.ui.window.widget = parent = object()
    viewer.inspect_selected_area.side_effect = ScalarMeasurementError("Select exactly one scene object to inspect area.")
    viewer.inspect_selected_volume.side_effect = RuntimeError("backend failed")

    assert inspect_selected_area(viewer) is None
    assert inspect_selected_volume(viewer) is None
    information.assert_called_once_with(parent, "Could Not Inspect Area", "Select exactly one scene object to inspect area.")
    critical.assert_called_once_with(parent, "Could Not Inspect Volume", "backend failed")
