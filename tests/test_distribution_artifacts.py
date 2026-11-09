import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / ".github" / "verify_distributions.py"
SPEC = importlib.util.spec_from_file_location("verify_distributions", SCRIPT)
assert SPEC and SPEC.loader
verify_distributions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_distributions)


METADATA = b"""Metadata-Version: 2.4
Name: compas_viewer
Version: 2.0.2
Requires-Python: >=3.12
Requires-Dist: compas<4,>=3
Requires-Dist: freetype-py
Requires-Dist: Pillow
Requires-Dist: PyOpenGL
Requires-Dist: PySide6
"""
ENTRY_POINTS = b"""[compas.plugins]
compas_viewer = compas_viewer.plugins
"""
WHEEL = b"""Wheel-Version: 1.0
Generator: test
Root-Is-Purelib: true
Tag: py3-none-any
"""


def write_wheel(directory, *, include_assets=True, excluded_asset=None, metadata=METADATA, entry_points=ENTRY_POINTS):
    wheel = directory / "compas_viewer-2.0.2-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("compas_viewer/__init__.py", "")
        if include_assets:
            for name in verify_distributions.REQUIRED_WHEEL_FILES:
                if name != excluded_asset:
                    archive.writestr(name, "asset")
        archive.writestr("compas_viewer-2.0.2.dist-info/METADATA", metadata)
        archive.writestr("compas_viewer-2.0.2.dist-info/entry_points.txt", entry_points)
        archive.writestr("compas_viewer-2.0.2.dist-info/WHEEL", WHEEL)
    return wheel


def write_sdist(directory, *, include_icon=True):
    sdist = directory / "compas_viewer-2.0.2.tar.gz"
    names = [
        "CHANGELOG.md",
        "LICENSE",
        "README.md",
        "pyproject.toml",
        "src/compas_viewer/plugins.py",
        "src/compas_viewer/py.typed",
        "src/compas_viewer/assets/fonts/FreeSans.ttf",
        "src/compas_viewer/renderer/shaders/model.vert",
    ]
    if include_icon:
        names.append("src/compas_viewer/assets/icons/compas_icon_white.png")
    with tarfile.open(sdist, "w:gz") as archive:
        for name in names:
            info = tarfile.TarInfo(f"compas_viewer-2.0.2/{name}")
            info.size = 0
            archive.addfile(info, io.BytesIO())
    return sdist


def test_distribution_verification_accepts_complete_artifacts(tmp_path):
    write_wheel(tmp_path)
    write_sdist(tmp_path)
    verify_distributions.verify_distributions(tmp_path)


def test_distribution_verification_requires_exact_artifact_set(tmp_path):
    write_wheel(tmp_path)
    with pytest.raises(ValueError, match="exactly one wheel"):
        verify_distributions.verify_distributions(tmp_path)


def test_distribution_verification_rejects_missing_package_data(tmp_path):
    wheel = write_wheel(tmp_path, include_assets=False)
    with pytest.raises(ValueError, match="package data"):
        verify_distributions.verify_wheel(wheel)


def test_distribution_verification_requires_runtime_icon_in_wheel(tmp_path):
    wheel = write_wheel(tmp_path, excluded_asset="compas_viewer/assets/icons/compas_icon_white.png")

    with pytest.raises(ValueError, match="compas_icon_white.png"):
        verify_distributions.verify_wheel(wheel)


def test_distribution_verification_requires_runtime_icon_in_sdist(tmp_path):
    sdist = write_sdist(tmp_path, include_icon=False)

    with pytest.raises(ValueError, match="compas_icon_white.png"):
        verify_distributions.verify_sdist(sdist)


def test_distribution_verification_rejects_wrong_runtime_dependency(tmp_path):
    metadata = METADATA.replace(b"compas<4,>=3", b"compas>=2")
    wheel = write_wheel(tmp_path, metadata=metadata)
    with pytest.raises(ValueError, match="runtime dependencies"):
        verify_distributions.verify_wheel(wheel)


def test_distribution_verification_rejects_missing_plugin_entry_point(tmp_path):
    wheel = write_wheel(tmp_path, entry_points=b"")
    with pytest.raises(ValueError, match="plugin entry point"):
        verify_distributions.verify_wheel(wheel)
