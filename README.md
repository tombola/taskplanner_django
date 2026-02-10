# Task planner

A simple django/wagtail app that provides business logic integrations with task management services
(initially only supporting ToDoist), in order to create tasks, provide an
overview of created tasks, and respond to webhooks.

## Setup

### Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
uv sync                        # Install all dependencies
cp .env.example .env           # Configure environment variables
uv run python manage.py migrate  # Apply database migrations
```

### Pre-commit hooks

This project uses [pre-commit](https://pre-commit.com/) to run ruff linting and formatting before each commit.

```bash
uv run task pre_commit         # Install git pre-commit hooks
```

## Development

### Running the server

```bash
uv run python manage.py runserver
```

### Available tasks

Run tasks with `uv run task <name>`:

| Task | Description |
|------|-------------|
| `pre_commit` | Install pre-commit hooks |
| `lint` | Run ruff linter |
| `lint_fix` | Run ruff linter with auto-fix |
| `format` | Format code with ruff |
| `format_check` | Check code formatting |
| `test` | Run all tests |
| `test_webhook` | Run webhook tests only |
| `bump_patch` | Bump patch version (0.1.0 -> 0.1.1) |
| `bump_minor` | Bump minor version (0.1.0 -> 0.2.0) |
| `bump_major` | Bump major version (0.1.0 -> 1.0.0) |
