from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

from compas_viewer.components.gridunitsetting import GridUnitSetting
from compas_viewer.config import Config
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_settings_items


def test_grid_unit_panel_updates_grid_and_measurement_presentation(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    viewer = SimpleNamespace(config=config, state=state)
    monkeypatch.setattr(GridUnitSetting, "viewer", property(lambda _self: viewer), raising=False)

    panel = GridUnitSetting()
    panel.unit_edit.setText(" mm ")
    panel.unit_edit.editingFinished.emit()
    panel.precision_edit.setText("5")
    panel.precision_edit.editingFinished.emit()
    state.set("renderer.show_grid", False)
    state.set("renderer.gridsize", (20.0, 8, 30.0, 12))

    assert config.measurement.unit == "mm"
    assert config.measurement.precision == 5
    assert panel.unit_edit.text() == "mm"
    assert not panel._state_controls["renderer.show_grid"].checkbox.isChecked()
    assert (panel.grid.dx, panel.grid.nx, panel.grid.dy, panel.grid.ny) == (20.0, 8.0, 30.0, 12.0)
    assert not hasattr(panel, "tolerance_owner")
    assert not hasattr(panel, "tolerance_labels")
    assert app is not None


def test_grid_unit_panel_synchronizes_explicit_external_measurement_changes(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    viewer = SimpleNamespace(config=config, state=state)
    monkeypatch.setattr(GridUnitSetting, "viewer", property(lambda _self: viewer), raising=False)
    panel = GridUnitSetting()

    state.set_measurement_unit("cm")
    state.set_measurement_precision(2)

    assert panel.unit_edit.text() == "cm"
    assert panel.precision_edit.text() == "2"
    assert app is not None


def test_grid_unit_precision_accepts_boundaries_and_restores_rejected_input(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    changes = []
    state.changed.connect(lambda path, value: changes.append((path, value)))
    viewer = SimpleNamespace(config=config, state=state)
    monkeypatch.setattr(GridUnitSetting, "viewer", property(lambda _self: viewer), raising=False)
    panel = GridUnitSetting()

    panel.precision_edit.setText("15")
    panel.precision_edit.editingFinished.emit()
    assert config.measurement.precision == 15
    assert panel.precision_edit.text() == "15"

    for rejected in ("16", "-1", "", "not-an-integer"):
        panel.precision_edit.setText(rejected)
        panel.precision_edit.editingFinished.emit()
        assert config.measurement.precision == 15
        assert panel.precision_edit.text() == "15"

    panel.precision_edit.setText("0")
    panel.precision_edit.editingFinished.emit()
    assert config.measurement.precision == 0
    assert panel.precision_edit.text() == "0"
    assert changes == [("measurement.precision", 15), ("measurement.precision", 0)]
    assert app is not None


def test_default_settings_contains_one_grid_and_units_panel():
    item_types = [item["type"] for item in default_settings_items()]

    assert item_types.count("GridUnitSetting") == 1
    assert "MeasurementSetting" not in item_types
