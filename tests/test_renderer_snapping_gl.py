import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _native_measurement_acquisition(report_path: Path) -> None:
    report_path.write_text(
        json.dumps(
            {
                "status": "starting",
                "availability": {
                    "system": sys.platform,
                    "requested_qt_platform": os.environ.get("QT_QPA_PLATFORM"),
                },
            }
        )
    )
    from OpenGL import GL
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QGuiApplication

    from compas.datastructures import Mesh
    from compas.geometry import Point
    from compas_viewer import Viewer
    from compas_viewer.config import Config
    from compas_viewer.plugins import register_scene_operations

    register_scene_operations()
    config = Config()
    config.window.width = 512
    config.window.height = 512
    config.renderer.show_grid = False
    config.renderer.view = "top"
    config.ui.menubar.show = False
    config.ui.toolbar.show = False
    config.ui.statusbar.show = False
    config.ui.sidebar.show = False
    config.ui.sidedock.show = False
    viewer = Viewer(config)
    scene = viewer.scene

    def quad(cx: float, cy: float, z: float = 0.0) -> Mesh:
        return Mesh.from_vertices_and_faces(
            [
                [cx - 0.5, cy - 0.5, z],
                [cx + 0.5, cy - 0.5, z],
                [cx + 0.5, cy + 0.5, z],
                [cx - 0.5, cy + 0.5, z],
            ],
            [[0, 1, 2, 3]],
        )

    face = scene.add(quad(-6, 3), show_points=False, show_lines=False, show_faces=True)
    edge = scene.add(
        Mesh.from_vertices_and_faces([[-3.5, 2.5, 0], [-2.5, 2.5, 0], [-3, 3.5, 0]], [[0, 1, 2]]),
        show_points=False,
        show_lines=True,
        show_faces=False,
    )
    hidden = scene.add(quad(0, 3), show=False, show_points=False, show_lines=False, show_faces=True)
    hidden_parent = scene.add_group(name="Hidden", show=False)
    ancestor_hidden = scene.add(quad(3, 3), parent=hidden_parent, show_points=False, show_lines=False, show_faces=True)
    empty = scene.add(quad(6, 3), show_points=False, show_lines=False, show_faces=False)
    depth_mesh = Mesh.from_vertices_and_faces(
        [
            [-4.75, -3.75, 0],
            [-3.25, -3.75, 0],
            [-3.25, -2.25, 0],
            [-4.75, -2.25, 0],
            [-4, -3, -1],
        ],
        [[0, 1, 2, 3]],
    )
    depth = scene.add(depth_mesh, show_points=False, show_lines=False, show_faces=True)
    occluded = scene.add(
        Mesh.from_vertices_and_faces([[0, -3, 0], [-0.75, -3.75, 0], [0.75, -3.75, 0]], [[0, 1, 2]]),
        show_points=False,
        show_lines=True,
        show_faces=False,
    )
    scene.add(quad(0, -3, 1), show_points=False, show_lines=False, show_faces=True)

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
            "system": sys.platform,
            "requested_qt_platform": os.environ.get("QT_QPA_PLATFORM"),
            "active_qt_platform": QGuiApplication.platformName(),
            "surface_created": window.windowHandle() is not None,
            "widget_valid": renderer.isValid(),
            "context_created": context is not None,
            "context_valid": context is not None and context.isValid(),
        }
        if not availability["surface_created"] or not availability["context_valid"]:
            report_path.write_text(
                json.dumps(
                    {
                        "status": "unavailable",
                        "reason": "Qt did not create a valid window surface and OpenGL context.",
                        "availability": availability,
                    }
                )
            )
            return

        report_path.write_text(json.dumps({"status": "available", "availability": availability}))

        renderer.makeCurrent()
        try:
            version = GL.glGetString(GL.GL_VERSION)
            version_text = version.decode() if version is not None else "unknown"
        finally:
            renderer.doneCurrent()

        renderer.camera.reset_position(view="top")
        renderer.camera.distance = 10
        renderer.update_projection()
        renderer.update()
        viewer.app.processEvents()
        viewer.state.measurement.start("inspection")

        def winner_at(point: Point) -> str | None:
            projection = renderer.project_point(point)
            assert projection is not None
            query = renderer.query_snap_context_at((projection.x, projection.y), 18.0)
            return str(query.winner.object_guid) if query.winner is not None else None

        cases = {
            "face_only": winner_at(Point(-6.5, 2.5, 0)),
            "edge_only": winner_at(Point(-3.5, 2.5, 0)),
            "whole_object_hidden": winner_at(Point(-0.5, 2.5, 0)),
            "ancestor_hidden": winner_at(Point(2.5, 2.5, 0)),
            "empty_representation": winner_at(Point(5.5, 2.5, 0)),
            "front_silhouette": winner_at(Point(-4.75, -3.75, 0)),
            "back_depth_mismatch": winner_at(Point(-4, -3, -1)),
            "external_occlusion": winner_at(Point(0, -3, 0)),
        }
        renderer.rendermode = "wireframe"
        cases["face_only_wireframe"] = winner_at(Point(-6.5, 2.5, 0))
        report_path.write_text(
            json.dumps(
                {
                    "status": "passed",
                    "availability": availability,
                    "version": version_text,
                    "cases": cases,
                    "guids": {
                        "face": str(face.guid),
                        "edge": str(edge.guid),
                        "depth": str(depth.guid),
                        "hidden": str(hidden.guid),
                        "ancestor_hidden": str(ancestor_hidden.guid),
                        "empty": str(empty.guid),
                        "occluded": str(occluded.guid),
                    },
                }
            )
        )
    finally:
        window.hide()
        viewer.app.processEvents()
        viewer.running = False


def test_native_gl_measurement_acquisition_visibility_matrix(tmp_path):
    report_path = tmp_path / "adr034-native-gl.json"
    environment = os.environ.copy()
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--adr034-native-gl", str(report_path)],
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
            pytest.fail("The real OpenGL acquisition path failed after creating a valid context:\n" + result.stdout + result.stderr)
        if report is not None and report.get("status") == "unavailable":
            pytest.skip(f"Real Qt/OpenGL is unavailable: {report['reason']} {report['availability']}")
        startup_error = (result.stdout + result.stderr).lower()
        unavailable_signatures = (
            "no screens available",
            "could not connect to display",
            "could not load the qt platform plugin",
            "no qt platform plugin could be initialized",
            "failed to create opengl context",
            "failed to create platform opengl context",
            "qopenglwidget: failed to create context",
            "does not support createplatformopenglcontext",
        )
        if any(signature in startup_error for signature in unavailable_signatures):
            pytest.skip(f"Qt could not start a window surface/OpenGL context on {sys.platform}: {result.stderr.strip()}")
        pytest.fail("The real OpenGL test process failed before reporting availability:\n" + result.stdout + result.stderr)
    assert report is not None, "The real OpenGL test process did not write its structured report."
    if report.get("status") == "unavailable":
        pytest.skip(f"Real Qt/OpenGL is unavailable: {report['reason']} {report['availability']}")
    assert report["status"] == "passed"

    cases = report["cases"]
    guids = report["guids"]
    assert report["version"] != "unknown"
    assert cases["face_only"] == guids["face"]
    assert cases["edge_only"] == guids["edge"]
    assert cases["front_silhouette"] == guids["depth"]
    assert cases["whole_object_hidden"] is None
    assert cases["ancestor_hidden"] is None
    assert cases["empty_representation"] is None
    assert cases["face_only_wireframe"] is None
    assert cases["back_depth_mismatch"] is None
    assert cases["external_occlusion"] is None


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "--adr034-native-gl":
    _native_measurement_acquisition(Path(sys.argv[2]))
