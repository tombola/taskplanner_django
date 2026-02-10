# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
This project uses `uv` for Python version and virtual environment management.

**Python Version**: Requires Python 3.13.x (not 3.14+)
- Python 3.14 introduced breaking changes to `dataclasses.field()` that are incompatible with the `dataclass-wizard` library used by `todoist-api-python`

```bash
# Install Python 3.13 if needed
uv python install 3.13

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
#   - tokens: Comma-separated list of tokens (e.g., SKU, VARIETYNAME)
#   - parent_task_title: Optional title template for parent task (uses template title if empty)
#   - description: Optional description template for parent task (prepended to template description)
#   - default_project_id: Optional project ID for task organization (uses inbox if empty)
```

## Architecture Notes

- Django project follows MTV (Model-Template-View) pattern
- Apps should be modular and focused on specific functionality
- Models define database schema using Django ORM
- Views handle request/response logic
- URLs are configured in `urls.py` files at project and app levels
- Admin interface configured in `admin.py` files for each app
- Tests use pytest with pytest-django plugin

### TodoSync Package Integration

This project uses the `todosync` Django package for generic task management features:

**Package Location:** `/Users/tom/projects/experiments/taskplanner/todosync_django`
**Installed as:** Editable dependency via `uv add --editable ../todosync_django`

#### Division of Responsibilities

**Todosync Package (Generic Features):**
- `BaseTaskGroupTemplate` - Base Wagtail Page model for task templates
- `TaskSyncSettings` - Site-wide configuration (tokens, default project ID)
- `LabelActionRule` - Label-based routing rules for webhooks
- `TaskGroup` - Tracks created task instances
- `TaskBlock` - StreamField block for task definitions
- Token substitution utilities
- Generic views for task creation; Todoist API integration in `todoist_api.py`
- Management commands: `list_todoist_projects`, `list_todoist_sections`

**Taskplanner App (Domain-Specific):**
- `CropTaskTemplate` - Extends `BaseTaskGroupTemplate` with `bed` field
- `BiennialCropTaskTemplate` - Extends `CropTaskTemplate` with `bed_second_year` field
- Application-specific business rules and validation
- Custom templates extending package templates (if needed)

#### When to Add Code

**Add to Package if:**
- Works with ANY domain (not just agriculture/crops)
- Provides infrastructure for extension (base classes, hooks)
- Implements core patterns (token substitution, templates)

**Add to App if:**
- Specific to agriculture/crop planning
- Hardcoded business rules or crop-specific relationships
- References beds, varieties, crops, or SKUs by name

#### Multi-Table Inheritance

Models use concrete child tables with explicit joins:

```
BaseTaskGroupTemplate (todosync package)
└── CropTaskTemplate (tasks app)
    └── BiennialCropTaskTemplate (tasks app)
```

Each model creates its own database table. No generic foreign keys are used.
