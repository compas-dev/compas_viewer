# COMPAS Viewer Agent Guide

## Scope and Principles

These instructions apply to the entire repository.

- Modernize `compas_viewer` toward the current COMPAS Python, typing, documentation, and public-API conventions instead of preserving legacy patterns merely because they already exist.
- Preserve unrelated working-tree changes and keep patches focused.
- Prefer the simplest implementation that expresses the required contract. Avoid speculative abstractions and compatibility layers.
- Breaking changes are acceptable when they materially improve architecture, API consistency, typing, or maintainability. Update internal consumers, tests, documentation, serialization contracts, and change notes together.
- Keep viewer concerns separated: scene objects adapt COMPAS data, renderers manage graphics resources and drawing, and UI components manage interaction and presentation.

## Python and Typing

- Support Python 3.12 and newer, as declared in `pyproject.toml`.
- Use modern Python syntax, zero-argument `super()`, PEP 604 unions, built-in generics, and `Self` for subclass-preserving returns.
- Annotate the values accepted by the runtime API. Do not add conversions or validation merely to satisfy a type checker.
- Prefer precise structural types and protocols over `Any`, concrete runtime type checks, or casts. Use `cast` only when a valid runtime invariant cannot be expressed cleanly.
- Use overloads when arguments determine a public return type.
- Use `TYPE_CHECKING` for dependencies imported only for annotations, especially Qt, OpenGL, optional, or heavy dependencies.
- Preserve COMPAS plugin discovery and avoid importing optional GUI or graphics dependencies earlier than necessary.
- Prefer NumPy-backed data where it materially improves rendering or interoperability, but avoid conversions when consumers can use existing buffers directly.

## Python Semantics and Runtime Contracts

- Prefer standard Python protocols, iteration, unpacking, comprehensions, context managers, properties, and special methods over custom equivalents.
- Prefer duck typing. Check concrete runtime types only when identity determines semantics, resolves a real ambiguity, or protects a documented invariant.
- Use EAFP when the operation already provides the correct failure behavior.
- Let indexing, unpacking, arithmetic, dictionary access, and function calls raise their natural exceptions instead of duplicating those checks.
- Preserve valid-input behavior, return types, ordering, scene hierarchy, rendering output, side effects, and documented errors unless a change is intentional and scoped.
- Release OpenGL and Qt resources deterministically. Keep ownership and lifecycle boundaries explicit.
- Prefer fixing an annotation or API boundary over changing values inside rendering or geometry algorithms.

## Class Organization

Organize substantial class bodies in this order:

1. data and serialization hooks
2. dunder methods
3. properties
4. alternative constructors
5. conversions
6. regular public methods
7. rendering or transformation methods
8. private helpers

Keep property accessors and overload groups together. Use specialized subsections only when they improve navigation.

## Documentation and Public API

- Modernize documentation and docstrings toward MkDocs/mkdocstrings-compatible NumPy style using Markdown.
- Every direct `compas_viewer.*` package initializer should define an explicit `__all__`; imports and `__all__` together define the official public API.
- Omit parameter types already present in signatures. Keep explicit canonical Python types in `Returns` sections.
- Document a tuple as one tuple return matching its annotation. For overloads, document each return and the argument condition selecting it.
- Omit `Returns` for functions returning `None`, and remove empty sections.
- Use backticks for code and identifiers, Markdown links and footnotes, and `$...$` or `$$...$$` for mathematics. Do not introduce new Sphinx roles, directives, citations, or math syntax.
- Format `See Also` as a NumPy-style section using mkdocstrings references.
- Keep executable examples valid as doctests.
- Document public dunder behavior, alternative constructors, and every public property. Explain copying, normalization, resource invalidation, and coupled setter side effects when relevant.
- Do not add manual `Attributes` sections when mkdocstrings can generate them.
- Except for single-line docstrings, leave a blank line before closing quotes.

## Tests and Validation

- Run the smallest relevant tests first, then broaden validation in proportion to risk.
- Use the repository commands documented in `CONTRIBUTING.md`, including `invoke test`, `invoke check`, `invoke docs`, and `invoke format`, where applicable.
- Focused Pytest, Ruff, and Pyright commands are appropriate during development.
- Always run `git diff --check` for changed patches.
- For typing work, supplement runtime tests with focused static or AST checks where annotations may otherwise be missed.
- Test public behavior rather than implementation metadata. Cover construction, scene and collection behavior, configuration, events, resource lifecycles, transformations, failure boundaries, and subclass-preserving constructors as applicable.
- Build the relevant documentation pages when changes can affect rendered API documentation, signatures, or section parsing.
