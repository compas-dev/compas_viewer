import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _native_torus_resolution_edit(report_path: Path) -> None:
    report_path.write_text(json.dumps({"status": "starting", "system": sys.platform}))

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtTest import QTest

    from compas.geometry import Torus
    from compas_viewer import Viewer
    from compas_viewer.components.objectsetting import ObjectSetting
    from compas_viewer.config import Config

    config = Config()
    config.window.width = 512
    config.window.height = 512
    config.ui.menubar.show = False
    config.ui.toolbar.show = False
    config.ui.statusbar.show = False
    config.ui.sidebar.show = False
    config.ui.sidedock.show = False
    viewer = Viewer(config)
    sceneobject = viewer.scene.add(Torus(2.0, 0.5), u=16, v=16)
    window = viewer.ui.window.widget
    renderer = viewer.renderer
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    renderer.setFixedSize(512, 512)
    window.resize(512, 512)
    viewer.running = True
    try:
        window.show()
        viewer.app.processEvents()
        context = renderer.context()
        availability = {
            "requested_qt_platform": os.environ.get("QT_QPA_PLATFORM"),
            "active_qt_platform": QGuiApplication.platformName(),
            "surface_created": window.windowHandle() is not None,
            "widget_valid": renderer.isValid(),
            "context_valid": context is not None and context.isValid(),
        }
        if not availability["surface_created"] or not availability["context_valid"]:
            report_path.write_text(json.dumps({"status": "unavailable", "availability": availability}))
            return
        report_path.write_text(json.dumps({"status": "available", "availability": availability}))

        setting = ObjectSetting()
        setting.populate(sceneobject)
        u_control = next(control for control in setting.children if control.label.text() == "U Resolution")
        wireframe_control = next(control for control in setting.children if control.label.text() == "Show wireframe")
        u_control.spinbox.selectAll()
        QTest.keyClicks(u_control.spinbox, "64")
        assert sceneobject.u == 16
        QTest.keyClick(u_control.spinbox, Qt.Key.Key_Enter)
        viewer.app.processEvents()
        initial_wireframe = sceneobject.show_lines
        wireframe_control.checkbox.click()
        viewer.app.processEvents()

        render_object = viewer.scene.render_object(sceneobject)
        report_path.write_text(
            json.dumps(
                {
                    "status": "passed",
                    "availability": availability,
                    "u": sceneobject.u,
                    "control_valid": u_control.spinbox.value() == 64,
                    "wireframe_toggled": sceneobject.show_lines is not initial_wireframe,
                    "vertices": len(render_object._frontfaces_data[0]),
                    "faces": len(render_object._frontfaces_data[2]),
                }
            )
        )
    finally:
        window.hide()
        viewer.app.processEvents()
        viewer.running = False


def test_native_gl_torus_resolution_keyboard_edit_does_not_crash(tmp_path):
    report_path = tmp_path / "torus-resolution-native-gl.json"
    environment = os.environ.copy()
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--native-torus-resolution", str(report_path)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    report = json.loads(report_path.read_text()) if report_path.is_file() else None
    if result.returncode != 0:
        if report is not None and report.get("status") == "available":
            pytest.fail("The native Torus resolution edit crashed after creating a valid OpenGL context:\n" + result.stdout + result.stderr)
        startup_error = (result.stdout + result.stderr).lower()
        unavailable = (
            "no screens available",
            "could not connect to display",
            "could not load the qt platform plugin",
            "no qt platform plugin could be initialized",
            "failed to create opengl context",
            "failed to create platform opengl context",
        )
        if any(signature in startup_error for signature in unavailable):
            pytest.skip(f"Qt could not create a native OpenGL context: {result.stderr.strip()}")
        pytest.fail("The native Torus resolution edit failed before reporting availability:\n" + result.stdout + result.stderr)
    assert report is not None
    if report["status"] == "unavailable":
        pytest.skip(f"Native Qt/OpenGL is unavailable: {report['availability']}")
    assert report["status"] == "passed"
    assert report["u"] == 64
    assert report["control_valid"]
    assert report["wireframe_toggled"]
    assert report["vertices"] > 0
    assert report["faces"] > 0


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "--native-torus-resolution":
    _native_torus_resolution_edit(Path(sys.argv[2]))
