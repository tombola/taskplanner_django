# Implementation Summary

## Project Structure

- **Django project**: `taskplanner` (project configuration)
- **Django app**: `tasks` (task management functionality)
- **Dependencies**: Django 5.2.8, Wagtail 7.2, pytest-django 4.11.1, todoist-api-python 3.1.0
- **Python version**: 3.14.0 (managed via uv)

## Core Components

### Models (`tasks/models.py`)

**TaskBlock** (Wagtail StreamField block)
- Defines structure for individual tasks with title, labels, and nested subtasks
- Uses recursive structure: subtasks are also TaskBlocks
- Tokens in titles use `{TOKEN_NAME}` format for substitution

**TaskGroupTemplate** (Wagtail Page model)
- Wagtail page type for creating task templates
- `tokens`: CharField containing comma-separated token names (e.g., "SKU, VARIETYNAME")
- `tasks`: StreamField containing TaskBlocks for the task structure
- `get_token_list()`: Helper method to parse comma-separated tokens into a list

**TaskPlannerSettings** (Wagtail Site Setting)
- Configurable in Wagtail admin under Settings → Task Planner Settings
- `debug_mode`: Boolean flag to enable debug mode (default: False)
  - When enabled, task creation prints debug info to stderr instead of posting to Todoist API
  - Useful for testing task templates without actually creating tasks in Todoist
  - Debug output shows task hierarchy, labels, and token substitution results

### Forms (`tasks/forms.py`)

**TaskGroupCreationForm**
- `task_group_template`: ModelChoiceField to select template
- Dynamically generates fields based on template's tokens
- When `template_id` is provided:
  - Pre-populates the `task_group_template` field with the specified template
  - Creates input fields named `token_{TOKEN_NAME}` for each token
- `get_token_values()`: Extracts token values from form submission

### Views (`tasks/views.py`)

**create_task_group**
- Renders form for task creation
- On template selection, reloads page with `template_id` to show token fields
- Checks `debug_mode` from TaskPlannerSettings
- On submission:
  - If debug mode enabled: prints task structure to stderr
  - If debug mode disabled: calls Todoist API to create tasks with token substitution
- Requires `TODOIST_API_TOKEN` in settings (only when debug mode is disabled)

**create_tasks_from_template**
- Iterates through template's tasks and creates them via API or prints debug info
- Accepts `debug` parameter to control behavior
- Prints debug header/footer when in debug mode

**create_task_recursive**
- Recursively creates tasks and subtasks
- Performs token substitution in titles: replaces `{TOKEN}` with provided values
- Parses comma-separated labels
- In normal mode: creates parent-child relationships for subtasks using `parent_id`
- In debug mode: prints indented task hierarchy with labels and mock IDs

### Templates

**tasks/templates/tasks/task_group_template.html**
- Display template for TaskGroupTemplate pages
- Shows tokens, task structure with subtasks, and labels
- Includes link to create tasks from the template
- Extends `base.html`

**tasks/templates/base.html**
- Base template with common layout
- Includes navigation, footer, and shared styles
- Custom CSS for task group template display

**tasks/templates/tasks/create_task_group.html**
- Form for selecting template and entering token values
- JavaScript event listener: when template selected, reloads page with `template_id` query param to dynamically show token input fields
- Displays success/error messages
- External CSS: `tasks/static/tasks/css/styles.css`

### URLs

**taskplanner/urls.py**
- Wagtail admin at `/admin/`
- Django admin at `/django-admin/`
- Tasks app at `/tasks/`
- Wagtail pages at `/`

**tasks/urls.py**
- `/tasks/create/`: Task group creation form

## Configuration

**Settings** (`taskplanner/settings.py`)
- Added Wagtail apps and dependencies to `INSTALLED_APPS`
- Added `wagtail.contrib.settings` to `INSTALLED_APPS` for admin-configurable settings
- Added `tasks` app to `INSTALLED_APPS`
- Added Wagtail redirect middleware
- Added `wagtail.contrib.settings.context_processors.settings` to template context processors
- Configured `WAGTAIL_SITE_NAME` and `WAGTAILADMIN_BASE_URL`
- Configured `MEDIA_ROOT` and `MEDIA_URL`

**Admin-configurable settings** (Wagtail Admin → Settings → Task Planner Settings):
- `debug_mode`: Enable debug mode to print task info instead of posting to Todoist

**Environment variables** (configure in `.env` file):
- `TODOIST_API_TOKEN`: API token for Todoist integration (required when debug mode is disabled)
  - Get your token from https://todoist.com/app/settings/integrations/developer
  - Copy `.env.example` to `.env` and add your token

## Workflow

1. Create TaskGroupTemplate pages in Wagtail admin
2. Define tokens (comma-separated) and task structure with nested subtasks
3. Navigate to `/tasks/create/`
4. Select template from dropdown (page reloads showing token input fields)
5. Fill in token values
6. Submit form to create tasks via Todoist API

## Testing

**Test coverage** (`tasks/tests.py`)
- 18 tests for TaskGroupCreationForm and TaskGroupTemplate model
- Tests dynamic field generation based on tokens
- Tests form validation and token value extraction
- Tests template field pre-population when template_id is provided
- Tests model's `get_token_list()` method with various inputs
- Tests Wagtail hooks for applying default tokens
- Uses pytest with pytest-django plugin
- Run tests: `uv run pytest tasks/tests.py -v`

**Test fixtures**
- `wagtail_site`: Creates/retrieves Wagtail site for testing
- `task_group_template`: Creates template with tokens and nested subtasks
- `empty_template`: Creates template without tokens for edge case testing

## Implementation Notes

**Subtasks structure**: Uses `blocks.ListBlock` with inline `StructBlock` definition instead of recursive `TaskBlock` references to avoid infinite recursion during model initialization. Subtasks support one level of nesting.

## Not Implemented

- Webhook endpoint for status changes (as noted in plan.md)
- Error handling for API failures beyond basic messaging
- Task tracking/history in database
- Authentication/authorization
- Deep nesting of subtasks (currently limited to one level)
