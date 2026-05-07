# Agent Guide for Fermi Problems

This document provides instructions for LLMs and other agents working on this codebase.

## Environment Management

This project uses `uv` for dependency management. **Always use `uv run`** (or the `$(VENV)` variable in the Makefile) to execute commands. This ensures that you are using the project's virtual environment and not polluting the system Python.

- **DO NOT** use `pip install`. Use `uv add`.
- **DO NOT** use `python ...` directly if a virtual environment is preferred. Use `uv run python ...`.

## Makefile Workflows

The `Makefile` contains common workflows. For LLM efficiency, use the `*-llm` targets which are designed to provide concise, token-efficient output.

### Essential Commands

- `make check-llm`: Runs linting, type checking, and tests with minimal output. This is the preferred way to verify changes.
- `make lint-llm`: Runs `ruff` check. Fast and concise.
- `make typecheck-llm`: Runs `mypy`.
- `make test-llm`: Runs `pytest` with short tracebacks and quiet output.

### Standard Commands (Higher Output)

- `make test`: Full test suite with coverage and verbose output.
- `make pylint`: Strict linting with `pylint`.
- `make mypy`: Full type checking.
- `make format`: Runs `isort` and `black`.

## Project Structure

- `fermi_problems/`: Core library logic.
- `tests/`: Unit and integration tests.
- `docs/`: Project documentation.

## Guidelines

- **Surgical Changes**: Prefer small, targeted edits.
- **Verification**: Always run `make check-llm` after making changes.
- **Documentation**: Update docstrings and `docs/` if you change public APIs.
- **Dependencies**: If you need a new library, use `uv add`. If it's for development, use `uv add --dev`.
