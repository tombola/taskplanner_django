# Implementation Summary

## Project Structure

- **Django project**: `taskplanner` (project configuration)
- **Django app**: `tasks` (task management functionality)
- **Dependencies**: Django 5.2.8, Wagtail 7.2, pytest-django 4.11.1, todoist-api-python 3.1.0
- **Python version**: 3.13.x (managed via uv)
  - **Note**: Python 3.14 is not supported due to incompatibility with dataclass-wizard (used by todoist-api-python). The `doc` parameter was added to `dataclasses.field()` in Python 3.14, breaking dataclass-wizard 0.35.1.

## Core Components

### Models (`tasks/models.py`)

**TaskBlock** (Wagtail StreamField block)
- Defines structure for individual tasks with title, labels, and nested subtasks
- Uses recursive structure: subtasks are also TaskBlocks
- Tokens in titles use `{TOKEN_NAME}` format for substitution

**TaskPlannerSettings** (Wagtail Site Setting)
- Site-wide settings configurable in Wagtail admin under Settings → Task Planner Settings
- `tokens`: CharField containing comma-separated token names (e.g., "SKU, VARIETYNAME")
- `parent_task_title`: Optional title template for parent task (can use tokens). If empty, uses template page title
- `description`: Optional description template for parent task (can use tokens). Prepended to template description
- `get_token_list()`: Helper method to parse comma-separated tokens into a list

**TaskGroupTemplate** (Wagtail Page model)
- Wagtail page type for creating task templates
- `description`: Optional description for the template (can use tokens). Appended to site-wide description
- `tasks`: StreamField containing TaskBlocks for the task structure
- Tokens are defined in TaskPlannerSettings (site-wide), not per-page

### Forms (`tasks/forms.py`)

**TaskGroupCreationForm**
- `task_group_template`: ModelChoiceField to select template
- `description`: Optional textarea for additional description (can use tokens). Appended to site and template descriptions
- Dynamically generates fields based on tokens from TaskPlannerSettings (site-wide)
- When `template_id` and `site` are provided:
  - Pre-populates the `task_group_template` field with the specified template
  - Reads tokens from TaskPlannerSettings for the site
  - Creates input fields named `token_{TOKEN_NAME}` for each token
- `get_token_values()`: Extracts token values from form submission

### Views (`tasks/views.py`)

**create_task_group**
- Renders form for task creation
- On template selection, reloads page with `template_id` to show token fields
- Displays task structure preview when a template is selected, showing:
  - All tasks that will be created
  - Subtasks for each task
  - Labels for tasks and subtasks
- Checks `DEBUG_TASK_CREATION` from Django settings
- On submission:
  - If debug mode enabled: prints task structure to stderr
  - If debug mode disabled: calls Todoist API to create tasks with token substitution
- Requires `TODOIST_API_TOKEN` environment variable (only when debug mode is disabled)

**create_tasks_from_template**
- Creates a parent task using either:
  - `parent_task_title` from TaskPlannerSettings (if configured), or
  - Template page title as fallback
- Builds parent task description by combining (in order):
  1. Site-wide description from TaskPlannerSettings
  2. Template description from TaskGroupTemplate
  3. Form description from TaskGroupCreationForm
  - All separated by double newline, all support token substitution
- Applies token substitution to both title and description
- Iterates through template's tasks and creates them as subtasks of the parent task
- Accepts `site` parameter to access settings
- Accepts `form_description` parameter from the creation form
- Accepts `debug` parameter to control behavior
- Prints debug header/footer when in debug mode (includes description in output)

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
- Displays task structure preview when template is selected:
  - Shows all tasks and subtasks that will be created
  - Displays labels for each task/subtask
  - Provides visual hierarchy with indentation and styling
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
- Added `tasks` app to `INSTALLED_APPS`
- Added Wagtail redirect middleware
- Configured `WAGTAIL_SITE_NAME` and `WAGTAILADMIN_BASE_URL`
- Configured `MEDIA_ROOT` and `MEDIA_URL`
- Configured `python-dotenv` to load environment variables from `.env` file
- Added `TODOIST_API_TOKEN` and `DEBUG_TASK_CREATION` settings from environment variables

**Environment variables** (configure in `.env` file):
- `TODOIST_API_TOKEN`: API token for Todoist integration (required when debug mode is disabled)
  - Get your token from https://todoist.com/app/settings/integrations/developer
  - Copy `.env.example` to `.env` and add your token
- `DEBUG_TASK_CREATION`: Enable debug mode to print task info instead of posting to Todoist (default: False)
  - Set to `True`, `1`, or `yes` to enable debug mode
  - Useful for testing task templates without creating actual tasks

## Workflow

1. Configure site-wide settings in Wagtail admin (Settings → Task Planner Settings):
   - Define tokens (comma-separated, e.g., "SKU, VARIETYNAME")
   - Optionally define parent_task_title template (e.g., "Plant {VARIETYNAME}")
   - Optionally define description template (e.g., "Variety: {VARIETYNAME}")
2. Create TaskGroupTemplate pages in Wagtail admin
3. Define template description (optional, can use tokens)
4. Define task structure with nested subtasks (tokens from site settings can be used)
5. Navigate to `/tasks/create/`
6. Select template from dropdown (page reloads showing token input fields based on site settings)
7. Fill in token values
8. Optionally add a form-specific description (can use tokens)
9. Submit form to create tasks via Todoist API:
   - The parent task uses `parent_task_title` from settings (or template page title as fallback)
   - Parent task description combines: site description + template description + form description (all tokenized)
   - All tasks defined in the template become subtasks of the parent task
   - Subtasks defined within tasks become nested subtasks

**Example hierarchy:**
```
Settings:
  - Tokens: "SKU, VARIETYNAME"
  - Parent Task Title: "Plant {VARIETYNAME}"
  - Description: "SKU: {SKU}\nVariety: {VARIETYNAME}"

Template: "Tomato Template"
Template Description: "This is the standard planting workflow for {VARIETYNAME}."
Tasks in template:
  - "Sow seeds"
    - "Prepare soil"
    - "Plant seeds"
  - "Water plants"

Form input:
  - SKU="TOM001"
  - VARIETYNAME="Tomato"
  - Description="Planting date: 2025-03-15"

Result in Todoist:
└─ Plant Tomato                    (from parent_task_title setting)
   Description:
   SKU: TOM001
   Variety: Tomato

   This is the standard planting workflow for Tomato.

   Planting date: 2025-03-15

   ├─ Sow seeds                     (from template tasks)
   │  ├─ Prepare soil               (nested subtask)
   │  └─ Plant seeds                (nested subtask)
   └─ Water plants                  (from template tasks)
```

## Testing

**Test coverage** (`tasks/tests.py`)
- Tests for TaskGroupCreationForm and TaskPlannerSettings model
- Tests dynamic field generation based on tokens from site settings
- Tests form validation and token value extraction
- Tests template field pre-population when template_id is provided
- Tests TaskPlannerSettings `get_token_list()` method with various inputs
- Uses pytest with pytest-django plugin
- Run tests: `uv run pytest tasks/tests.py -v`

**Test fixtures**
- `wagtail_site`: Creates/retrieves Wagtail site for testing
- `planner_settings`: Creates TaskPlannerSettings with tokens
- `empty_planner_settings`: Creates TaskPlannerSettings without tokens
- `task_group_template`: Creates template with nested subtasks
- `empty_template`: Creates template without tokens in settings

## Implementation Notes

**Subtasks structure**: Uses `blocks.ListBlock` with inline `StructBlock` definition instead of recursive `TaskBlock` references to avoid infinite recursion during model initialization. Subtasks support one level of nesting.

## Not Implemented

- Webhook endpoint for status changes (as noted in plan.md)
- Error handling for API failures beyond basic messaging
- Task tracking/history in database
- Authentication/authorization
- Deep nesting of subtasks (currently limited to one level)
