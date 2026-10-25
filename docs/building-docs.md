# Building the Documentation

The documentation is built with MkDocs Material. API pages are generated from Python docstrings by mkdocstrings, and longer examples reuse source files through the snippets extension.

## Install the documentation environment

From the repository root, install the project with both development and documentation dependencies:

```bash
python -m pip install -e ".[dev,docs]"
```

This installs MkDocs, MkDocs Material, mkdocstrings, Pyright, Pytest, Ruff, Invoke, and the local `compas_viewer` package.

## Build the site

Use the repository task for the normal documentation build:

```bash
invoke docs
```

To remove the previous generated site before building:

```bash
invoke docs --clean
```

The generated HTML is written to `site/`. This directory is build output; edit files in `docs/` or source docstrings instead.

## Preview changes locally

Start MkDocs' development server from the repository root:

```bash
python -m mkdocs serve
```

Open <http://127.0.0.1:8000/>. MkDocs watches documentation, configuration, and imported source files and refreshes the site after changes.

Use a different address or port when necessary:

```bash
python -m mkdocs serve --dev-addr 127.0.0.1:9000
```

Stop the server with `Ctrl+C`.

## Run a strict build

Before submitting documentation changes, treat broken links, stale navigation, and other MkDocs warnings as errors:

```bash
python -m mkdocs build --strict
```

Also check Markdown code blocks, docstrings, and repository formatting:

```bash
invoke testcodeblocks
invoke testdocs
ruff check src tests
git diff --check
```

The documentation CI workflow installs Python 3.12 with the `docs` extra and runs `invoke docs` on pull requests and pushes to `main`.

## Documentation layout

| Location | Purpose |
| --- | --- |
| `docs/index.md` | Documentation homepage |
| `docs/hello-world.md` | Minimal first-run tutorial |
| `docs/user-guide.md` | Task-oriented user documentation |
| `docs/developer-guide.md` | Architecture and extension documentation |
| `docs/examples/` | Focused examples and their Python sources |
| `docs/api/` | mkdocstrings API entry pages |
| `docs/assets/images/` | Screenshots, diagrams, and animations |
| `docs/assets/logos/` | Project and product logos |
| `mkdocs.yml` | Site configuration and navigation |

Every page intended for normal navigation should be added to `nav` in `mkdocs.yml`. A strict build reports links to missing pages and invalid navigation entries.

## Add a guide or tutorial

1. Create a Markdown file under `docs/`.
2. Start with one level-one heading.
3. Organize the page around reader tasks rather than package internals.
4. Use relative links to other documentation pages.
5. Add the page to `nav` in `mkdocs.yml`.
6. Run the strict build.

For example:

```yaml
nav:
  - Guides:
      - My Guide: my-guide.md
```

## Add an example

Keep executable example code in a `.py` file and include it from the corresponding Markdown page:

```text
--8<-- "docs/examples/scene/groups.py"
```

For example, this structure keeps prose and runnable code together:

```text
docs/examples/scene/
├── groups.md
└── groups.py
```

Add the Markdown page—not the Python source—to the Examples navigation in `mkdocs.yml`. Run the Python file directly when checking runtime behavior, and use `invoke testcodeblocks` for fenced documentation examples.

## Add images and other assets

Put raster images and animations in `docs/assets/images/`. Put logos in `docs/assets/logos/`. Reference them relative to the Markdown page:

```markdown
![Viewer scene](assets/images/compas_viewer.png)
```

Use meaningful lowercase filenames. Prefer compressed PNG, JPEG, GIF, or WebP files appropriate to the content. Do not place generated screenshots in the repository root or in `site/`.

## Add API documentation

API pages use mkdocstrings directives:

```markdown
# `compas_viewer.example`

::: compas_viewer.example
```

Place the page in `docs/api/`, link it from `docs/api.md`, and add it to the API Reference navigation.

mkdocstrings reads source files from `src/`, as configured in `mkdocs.yml`. Public modules and package initializers should expose deliberate `__all__` lists so the generated reference reflects the supported API.

## Write source docstrings

Public Python APIs use MkDocs-compatible NumPy-style docstrings:

```python
def scale(value: float, factor: float = 1.0) -> float:
    """Scale a numeric value.

    Parameters
    ----------
    value
        Value to scale.
    factor
        Scale factor.

    Returns
    -------
    float
        Scaled value.

    """
    return value * factor
```

Keep types in Python annotations rather than repeating them in parameter descriptions. Except for one-line docstrings, leave a blank line before the closing quotes. Use Markdown links and backticks instead of Sphinx roles or directives.

## Troubleshooting

### `No module named mkdocs`

Install the documentation extra in the active environment:

```bash
python -m pip install -e ".[docs]"
```

Using `python -m mkdocs` ensures that MkDocs runs from the same environment as the selected Python interpreter.

### API imports fail

Install the project in editable mode with all documentation dependencies:

```bash
python -m pip install -e ".[dev,docs]"
```

Then verify that the active interpreter can import the package:

```bash
python -c "import compas_viewer; print(compas_viewer.__version__)"
```

### Strict builds report missing pages

Check both the path in `mkdocs.yml` and relative links in Markdown. Paths are relative to `docs/`, while snippet paths are checked from the repository root because `check_paths` is enabled.

### Linux CI cannot import OpenGL

The documentation workflow installs `libegl1` and `python3-opengl` before building. Install equivalent system OpenGL/EGL packages when reproducing that environment locally.
