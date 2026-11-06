from invoke import task


@task
def check(ctx):
    """Run all non-mutating local quality checks."""
    ctx.run("uv run ruff check .")
    ctx.run("uv run ruff format --check .")
    ctx.run("uv run pyright")


@task
def lint(ctx):
    """Fix lint violations that Ruff can resolve safely."""
    ctx.run("uv run ruff check --fix .")


@task
def format(ctx):
    """Format Python files with Ruff."""
    ctx.run("uv run ruff format .")


@task
def test(ctx):
    """Run the test suite with the headless Qt backend."""
    ctx.run("uv run pytest", env={"QT_QPA_PLATFORM": "offscreen"})


@task
def docs(ctx):
    """Build the documentation in strict mode."""
    ctx.run("uv run mkdocs build --strict", env={"QT_QPA_PLATFORM": "offscreen"})
