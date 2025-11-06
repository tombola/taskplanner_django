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

### Forms (`tasks/forms.py`)

**TaskGroupCreationForm**
- `task_group_template`: ModelChoiceField to select template
- Dynamically generates fields based on template's tokens
- When `template_id` is provided, creates input fields named `token_{TOKEN_NAME}`
- `get_token_values()`: Extracts token values from form submission

### Views (`tasks/views.py`)

**create_task_group**
- Renders form for task creation
- On template selection, reloads page with `template_id` to show token fields
- On submission, calls Todoist API to create tasks with token substitution
- Requires `TODOIST_API_TOKEN` in settings

**create_tasks_from_template**
- Iterates through template's tasks and creates them via API

**create_task_recursive**
- Recursively creates tasks and subtasks
- Performs token substitution in titles: replaces `{TOKEN}` with provided values
- Parses comma-separated labels
- Creates parent-child relationships for subtasks using `parent_id`

### Templates

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
- Added `tasks` app to `INSTALLED_APPS`
- Added Wagtail redirect middleware
- Configured `WAGTAIL_SITE_NAME` and `WAGTAILADMIN_BASE_URL`
- Configured `MEDIA_ROOT` and `MEDIA_URL`

**Required environment variable**:
- `TODOIST_API_TOKEN`: API token for Todoist integration (to be added to settings)

## Workflow

1. Create TaskGroupTemplate pages in Wagtail admin
2. Define tokens (comma-separated) and task structure with nested subtasks
3. Navigate to `/tasks/create/`
4. Select template from dropdown (page reloads showing token input fields)
5. Fill in token values
6. Submit form to create tasks via Todoist API

## Not Implemented

- Webhook endpoint for status changes (as noted in plan.md)
- Error handling for API failures beyond basic messaging
- Task tracking/history in database
- Authentication/authorization
