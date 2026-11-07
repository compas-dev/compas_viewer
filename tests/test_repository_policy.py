import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
LOCKED_COMPAS_CANDIDATE = "d43db206afec36450efbe76b53306ce3bd468076"
SCENE_COMPAS_CANDIDATE = "d43db206afec36450efbe76b53306ce3bd468076"
COMPAS_ACTIONS = "5c64e6e2b576a1232d28fed47d9478ca8eb63b2d"


def workflow_text(name):
    return (WORKFLOWS / name).read_text()


def test_project_uses_locked_dependency_groups_and_compas_3():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert "optional-dependencies" not in project["project"]
    assert set(project["dependency-groups"]) == {"dev", "docs"}
    assert "compas>=3,<4" in project["project"]["dependencies"]
    assert project["tool"]["uv"]["sources"]["compas"]["rev"] == LOCKED_COMPAS_CANDIDATE
    assert project["tool"]["pyright"]["include"] == ["src/compas_viewer", "docs/examples"]
    assert "black" not in project["tool"]


def test_workflow_actions_are_immutable():
    for workflow in WORKFLOWS.glob("*.yml"):
        for action, revision in re.findall(r"uses:\s+([^@\s]+)@([^\s]+)", workflow.read_text()):
            assert re.fullmatch(r"[0-9a-f]{40}", revision), f"{workflow.name}: {action}@{revision}"


def test_quality_workflow_keeps_headless_graphics_provisioning_visible():
    workflow = workflow_text("build.yml")
    assert "QT_QPA_PLATFORM: offscreen" in workflow
    assert "apt-get install --yes libegl1 python3-opengl" in workflow
    assert "uv run --no-sync ruff check ." in workflow
    assert "uv run --no-sync ruff format --check ." in workflow
    assert "uv run --no-sync pyright" in workflow
    assert "uv run --no-sync pytest" in workflow
    assert "docs-only" not in workflow
    assert "ruff check --fix" not in workflow
    assert "remove-future" not in workflow
    assert SCENE_COMPAS_CANDIDATE in workflow
    assert f"compas-actions/setup-python@{COMPAS_ACTIONS}" in workflow


def test_authoritative_examples_have_declared_categories_and_no_temp_archive():
    examples = (ROOT / "docs" / "examples.md").read_text()
    assert "static-only interactive" in examples
    assert "static-and-smoke" in examples
    assert "static-plus-optional-runtime" in examples
    assert not (ROOT / "docs" / "examples" / "__temp").exists()


def test_documentation_and_release_workflows_are_strict_and_build_once():
    docs = workflow_text("docs.yml")
    release = workflow_text("release.yml")
    assert "QT_QPA_PLATFORM: offscreen" in docs
    assert "strict: true" in docs
    assert release.count("uv build --out-dir") == 1
    assert "needs: [detect, docs-build, prepare]" in release
    assert "needs: [detect, publish]" in release
    assert "pypa/gh-action-pypi-publish@dc37677b2e1c63e2034f94d8a5b11f265b73ba33" in release
    assert "id-token: write" in release


def test_artifact_workflows_verify_graphics_free_plugin_discovery():
    for name in ["build.yml", "release.yml"]:
        workflow = workflow_text(name)
        verifier = 'python" "${GITHUB_WORKSPACE}/.github/verify_plugin_discovery.py"'
        assert verifier in workflow
        assert workflow.index(verifier) < workflow.index("freetype-py Pillow PyOpenGL PySide6")
        assert "tests/installed_typing_consumer.py" in workflow
        assert 'python" -m pyright' in workflow


def test_invoke_tasks_are_thin_uv_aliases():
    tasks = (ROOT / "tasks.py").read_text()
    assert "compas_invocations" not in tasks
    for command in [
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run pyright",
        "uv run pytest",
        "uv run mkdocs build --strict",
    ]:
        assert command in tasks
