---
name: update-type-hints
description: Add, modernize, or review Python type hints in compas_viewer for Python 3.12+ without unintentionally changing runtime behavior.
---

# Update compas_viewer type hints

Apply the repository-wide rules in `AGENTS.md`, especially **Python and Typing**, **Python Semantics and Runtime Contracts**, and **Tests and Validation**.

## Requirements

- Use Python 3.12 syntax, including `X | Y` and `X | None` instead of `Union` and `Optional`.
- Prefer built-in generics such as `list[tuple[...]]` over legacy `typing` aliases.
- Use `Self` for methods and classmethods that preserve the receiver or subclass type.
- Use overloads for argument-dependent public return types instead of `Any`.
- Model the values accepted by the existing runtime API; do not add conversions or validation merely to satisfy an annotation.
- Prefer precise protocols, aliases, overloads, or source annotations over `cast`, concrete runtime type checks, or broad `Any`.
- Avoid runtime imports of optional or heavy dependencies used only for typing; use `TYPE_CHECKING` when necessary.
- Keep Qt, OpenGL, NumPy, and COMPAS types precise without weakening imports or changing plugin registration behavior.
- Preserve subclass behavior, defaults, accepted inputs, return values, ordering, rendering behavior, side effects, and exception behavior unless the task explicitly authorizes a change.

## Validation

Run the narrowest relevant tests first. Run a focused static type check when configured or available, Ruff on touched Python files, and `git diff --check`. Use AST-based searches when type comments or less obvious annotation sites may remain.
