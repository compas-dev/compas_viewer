# Installation

## Stable release

Install the latest stable release from PyPI:

```bash
python -m pip install compas_viewer
```

COMPAS Viewer requires Python 3.12 or newer, COMPAS 3, PySide6, and OpenGL.

## Development setup

Clone the repository and create the locked development and documentation
environment with uv:

```bash
git clone https://github.com/compas-dev/compas_viewer.git
cd compas_viewer
uv sync --frozen --group dev --group docs
```

Run the same checks used by continuous integration:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
QT_QPA_PLATFORM=offscreen uv run pytest
QT_QPA_PLATFORM=offscreen uv run mkdocs build --strict
```

The direct commands are authoritative. Thin Invoke aliases remain available,
for example `uv run invoke test` and `uv run invoke docs`.

## Linux graphics libraries

Linux development and continuous-integration environments need an explicit
EGL/OpenGL runtime. On Ubuntu, install:

```bash
sudo apt-get update
sudo apt-get install --yes libegl1 python3-opengl
```

The test and documentation commands select Qt's `offscreen` platform so that
they do not require a visible display. This does not replace platform-specific
testing of the interactive Qt/OpenGL viewer.
