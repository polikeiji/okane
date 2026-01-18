# Python Development Constitution

**Version**: 1.0.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-18

This document defines the mandatory principles and practices for all Python code in the Okane project.

## Core Principles

### I. Package Management with uv

**All Python projects MUST use `uv` as the package manager.**

- Use `uv` for all dependency management, installation, and virtual environment operations
- Project dependencies MUST be declared in `pyproject.toml`
- Pin exact versions for production dependencies
- Lock files MUST be committed to version control
- Document any deviations with explicit justification

**Rationale**: `uv` provides fast, reliable, and reproducible dependency management with better performance than traditional pip-based workflows.

### II. CLI Implementation with argparse

**All command-line tools MUST use `argparse` for argument parsing.**

- Use Python's standard library `argparse` module for all CLI applications
- Provide clear help text for all commands and arguments
- Follow consistent naming conventions for arguments (kebab-case for flags)
- Support `--help` and `-h` for all commands
- Provide meaningful error messages for invalid arguments

**Rationale**: `argparse` is the standard library solution, requires no additional dependencies, and provides robust, well-documented CLI parsing capabilities.

### III. Code Quality with ruff

**All Python code MUST be linted and formatted using `ruff`.**

- Run `ruff check` to lint code (replaces flake8, pylint, etc.)
- Run `ruff format` to format code (replaces black, autopep8, etc.)
- Ruff configuration MUST be defined in `pyproject.toml`
- All code MUST pass ruff checks before commit
- CI/CD pipelines MUST include ruff validation
- Pre-commit hooks SHOULD be configured to run ruff automatically

**Rationale**: `ruff` is an extremely fast linter and formatter written in Rust that consolidates multiple tools, providing comprehensive checking with minimal configuration.

### IV. Type Hints

**All Python code MUST include type hints for function signatures.**

- Use type hints for all function parameters and return values
- Use `typing` module for complex types (List, Dict, Optional, Union, etc.)
- Use modern type syntax (PEP 604) where supported: `str | None` instead of `Optional[str]`
- Run type checkers (mypy or pyright) in CI/CD
- Document any `# type: ignore` comments with justification

**Rationale**: Type hints improve code readability, enable better IDE support, catch errors early, and serve as inline documentation.

### V. Project Structure

**Python projects MUST follow a consistent directory structure.**

```
project-root/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── cli/
│       ├── models/
│       ├── services/
│       └── lib/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── pyproject.toml
├── README.md
└── .python-version (if needed)
```

- Source code MUST be in `src/` directory
- Tests MUST be in `tests/` directory, organized by type
- Package metadata and dependencies MUST be in `pyproject.toml`
- Use `__init__.py` to mark packages and control public API

### VI. Testing

**Python projects MUST use pytest for testing.**

- Use `pytest` as the testing framework
- Organize tests by type: unit, integration, contract
- Test files MUST be named `test_*.py` or `*_test.py`
- Achieve meaningful test coverage (target: >80% for core logic)
- Use fixtures for test setup and teardown
- Mock external dependencies in unit tests

**Rationale**: `pytest` is the de facto standard Python testing framework with excellent features, plugin ecosystem, and community support.

### VII. Documentation

**Python code MUST include docstrings following conventions.**

- Use Google-style or NumPy-style docstrings consistently
- All public modules, classes, and functions MUST have docstrings
- Include parameter descriptions, return value descriptions, and example usage
- Generate API documentation from docstrings
- Keep README.md up-to-date with installation and usage instructions

### VIII. Error Handling

**Python code MUST implement proper error handling.**

- Use specific exception types, avoid bare `except:` clauses
- Provide meaningful error messages
- Log errors with appropriate context
- Use context managers (`with` statements) for resource management
- Document expected exceptions in docstrings

### IX. Dependencies

**Minimize external dependencies and justify each addition.**

- Prefer standard library solutions when adequate
- Evaluate dependencies for:
  - Maintenance status and community support
  - Security track record
  - Performance characteristics
  - License compatibility
- Document rationale for each major dependency
- Regularly update dependencies for security patches

### X. Python Version

**Support modern, maintained Python versions.**

- Target Python 3.11+ for new projects
- Clearly document minimum Python version in `pyproject.toml` and README
- Use modern Python features and syntax where appropriate
- Test against supported Python versions in CI/CD

## Configuration

### pyproject.toml Structure

Every Python project MUST include a properly configured `pyproject.toml`:

```toml
[project]
name = "package-name"
version = "0.1.0"
description = "Brief description"
authors = [{name = "Author Name", email = "email@example.com"}]
requires-python = ">=3.11"
dependencies = [
    # List runtime dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.1.0",
    # Other dev dependencies
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
```

## Governance

This constitution applies to all Python code within the Okane project. Any exceptions must be:

1. Documented with clear justification
2. Reviewed and approved by maintainers
3. Tracked as technical debt if temporary

**Amendments**: Changes to this constitution require:
- Documentation of rationale
- Impact assessment on existing code
- Migration plan for breaking changes
- Version bump following semantic versioning

**Compliance**: All code reviews MUST verify compliance with this constitution.

**Related Documents**:
- Main Constitution: `.specify/memory/constitution.md`
- Plan Template: `.specify/templates/plan-template.md`
- Tasks Template: `.specify/templates/tasks-template.md`
