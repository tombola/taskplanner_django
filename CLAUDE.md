# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
This project uses `uv` for Python version and virtual environment management.

```bash
# Install dependencies
uv sync

# Copy example environment file and configure
cp .env.example .env
# Edit .env and add your TODOIST_API_TOKEN

# Run commands in the uv environment
uv run <command>
```

### Running the Application
```bash
# Run development server
uv run python manage.py runserver

# Run on specific port
uv run python manage.py runserver 8080
```

### Database Migrations
```bash
# Create migrations after model changes
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Show migration status
uv run python manage.py showmigrations
```

### Testing
This project uses pytest for testing.

```bash
# Run all tests
uv run pytest

# Run tests for specific app
uv run pytest <app_name>/

# Run specific test file
uv run pytest <path/to/test_file.py>

# Run specific test class or function
uv run pytest <path/to/test_file.py>::<TestClass>
uv run pytest <path/to/test_file.py>::<TestClass>::<test_method>

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov
```

### Django Shell
```bash
# Open Django shell
uv run python manage.py shell
```

### Django Admin
```bash
# Create superuser
uv run python manage.py createsuperuser
```

### Wagtail Admin
```bash
# Access Wagtail admin at http://localhost:8000/admin/
# Configure Task Planner settings: Settings → Task Planner Settings
#   - debug_mode: Enable to print debug info instead of posting to Todoist API
```

## Architecture Notes

- Django project follows MTV (Model-Template-View) pattern
- Apps should be modular and focused on specific functionality
- Models define database schema using Django ORM
- Views handle request/response logic
- URLs are configured in `urls.py` files at project and app levels
- Admin interface configured in `admin.py` files for each app
- Tests use pytest with pytest-django plugin
