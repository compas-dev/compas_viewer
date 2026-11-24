import sys
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.utils import parse_wheel_filename

PACKAGE = "compas_viewer"
EXPECTED_DEPENDENCIES = {
    "compas": "<4,>=3",
    "freetype-py": "",
    "pillow": "",
    "pyopengl": "",
    "pyside6": "",
}
REQUIRED_WHEEL_FILES = {
    "compas_viewer/py.typed",
    "compas_viewer/assets/fonts/FreeSans.ttf",
    "compas_viewer/assets/icons/compas_icon_white.png",
    "compas_viewer/renderer/shaders/model.frag",
    "compas_viewer/renderer/shaders/model.vert",
}


def find_distributions(directory: Path) -> tuple[Path, Path]:
    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("Expected exactly one wheel and one source distribution.")
    if not wheels[0].stat().st_size or not sdists[0].stat().st_size:
        raise ValueError("Distribution files must not be empty.")
    return wheels[0], sdists[0]


def _one_name(names: list[str], suffix: str) -> str:
    matches = [name for name in names if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Wheel must contain exactly one {suffix} file.")
    return matches[0]


def verify_wheel(wheel: Path) -> None:
    distribution, _, build, tags = parse_wheel_filename(wheel.name)
    if distribution != canonicalize_name(PACKAGE) or build or {str(tag) for tag in tags} != {"py3-none-any"}:
        raise ValueError("Wheel must be the expected pure-Python compas_viewer distribution.")

    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        missing = REQUIRED_WHEEL_FILES.difference(names)
        if missing:
            raise ValueError(f"Wheel is missing required package data: {sorted(missing)}")
        metadata = BytesParser().parsebytes(archive.read(_one_name(names, ".dist-info/METADATA")))
        entry_points = archive.read(_one_name(names, ".dist-info/entry_points.txt")).decode()
        wheel_metadata = archive.read(_one_name(names, ".dist-info/WHEEL")).decode()

    if metadata["Requires-Python"] != ">=3.12":
        raise ValueError("Wheel has an unexpected Requires-Python value.")

    requirements = {canonicalize_name(requirement.name): requirement for value in metadata.get_all("Requires-Dist", []) for requirement in [Requirement(value)]}
    actual = {name: str(requirement.specifier) for name, requirement in requirements.items()}
    if actual != EXPECTED_DEPENDENCIES:
        raise ValueError(f"Wheel has unexpected runtime dependencies: {actual}")
    if "[compas.plugins]" not in entry_points or "compas_viewer = compas_viewer.plugins" not in entry_points:
        raise ValueError("Wheel is missing the compas_viewer plugin entry point.")
    if "Root-Is-Purelib: true" not in wheel_metadata:
        raise ValueError("Wheel must be marked as pure Python.")


def verify_sdist(sdist: Path) -> None:
    with tarfile.open(sdist) as archive:
        names = archive.getnames()
    roots = {name.split("/", 1)[0] for name in names}
    if len(roots) != 1:
        raise ValueError("Source distribution must have one root directory.")
    root = roots.pop()
    required = {
        f"{root}/CHANGELOG.md",
        f"{root}/LICENSE",
        f"{root}/README.md",
        f"{root}/pyproject.toml",
        f"{root}/src/compas_viewer/plugins.py",
        f"{root}/src/compas_viewer/py.typed",
        f"{root}/src/compas_viewer/assets/fonts/FreeSans.ttf",
        f"{root}/src/compas_viewer/assets/icons/compas_icon_white.png",
        f"{root}/src/compas_viewer/renderer/shaders/model.vert",
    }
    missing = required.difference(names)
    if missing:
        raise ValueError(f"Source distribution is incomplete: {sorted(missing)}")


def verify_distributions(directory: Path) -> None:
    wheel, sdist = find_distributions(directory)
    verify_wheel(wheel)
    verify_sdist(sdist)


if __name__ == "__main__":
    verify_distributions(Path(sys.argv[1]))
