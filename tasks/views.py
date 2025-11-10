from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from todoist_api_python.api import TodoistAPI
from .models import TaskGroupTemplate
from .forms import TaskGroupCreationForm
import sys


def create_task_group(request):
    """View for creating task groups from templates"""

    template_id = request.GET.get('template_id') or request.POST.get('template_id')

    if request.method == 'POST':
        form = TaskGroupCreationForm(request.POST, template_id=template_id)

        if form.is_valid():
            template = form.cleaned_data['task_group_template']
            token_values = form.get_token_values()

            # Check debug mode from Django settings
            debug_mode = getattr(settings, 'DEBUG_TASK_CREATION', False)

            # Create tasks via Todoist API or debug print
            try:
                if debug_mode:
                    # Debug mode: print to console instead of posting
                    created_tasks = create_tasks_from_template(None, template, token_values, debug=True)
                    messages.success(request, f'DEBUG MODE: Printed {len(created_tasks)} tasks to console')
                else:
                    # Normal mode: post to Todoist API
                    api_token = getattr(settings, 'TODOIST_API_TOKEN', None)
                    if not api_token:
                        messages.error(request, 'Todoist API token not configured')
                        return redirect('tasks:create_task_group')

                    api = TodoistAPI(api_token)
                    created_tasks = create_tasks_from_template(api, template, token_values, debug=False)
                    messages.success(request, f'Successfully created {len(created_tasks)} tasks')

                return redirect('tasks:create_task_group')

            except Exception as e:
                messages.error(request, f'Error creating tasks: {str(e)}')

    else:
        form = TaskGroupCreationForm(template_id=template_id)

    return render(request, 'tasks/create_task_group.html', {
        'form': form,
        'template_id': template_id,
    })


def create_tasks_from_template(api, template, token_values, debug=False):
    """Create Todoist tasks from template with token substitution

    Args:
        api: TodoistAPI instance (can be None if debug=True)
        template: TaskGroupTemplate instance
        token_values: Dict of token replacements
        debug: If True, print debug info instead of posting to API
    """
    created_tasks = []

    if debug:
        print("\n" + "="*80, file=sys.stderr)
        print(f"DEBUG: Creating tasks from template: {template.title}", file=sys.stderr)
        print(f"DEBUG: Token values: {token_values}", file=sys.stderr)
        print("="*80 + "\n", file=sys.stderr)

    for task_data in template.tasks:
        if task_data.block_type == 'task':
            task_block = task_data.value
            created_task = create_task_recursive(api, task_block, token_values, debug=debug)
            if created_task:
                created_tasks.append(created_task)

    if debug:
        print("\n" + "="*80, file=sys.stderr)
        print(f"DEBUG: Total tasks created: {len(created_tasks)}", file=sys.stderr)
        print("="*80 + "\n", file=sys.stderr)

    return created_tasks


def create_task_recursive(api, task_block, token_values, parent_id=None, debug=False, indent=0):
    """Recursively create a task and its subtasks

    Args:
        api: TodoistAPI instance (can be None if debug=True)
        task_block: Task block data
        token_values: Dict of token replacements
        parent_id: Parent task ID (None for top-level tasks)
        debug: If True, print debug info instead of posting to API
        indent: Indentation level for debug output
    """

    # Substitute tokens in title
    title = task_block['title']
    for token, value in token_values.items():
        title = title.replace(f'{{{token}}}', value)

    # Parse labels
    labels = []
    if task_block.get('labels'):
        labels = [label.strip() for label in task_block['labels'].split(',') if label.strip()]

    # Create task via API or print debug info
    task_params = {
        'content': title,
    }

    # Only add labels if there are any
    if labels:
        task_params['labels'] = labels

    # Only add parent_id if it exists
    if parent_id:
        task_params['parent_id'] = parent_id

    if debug:
        # Debug mode: print task info
        indent_str = "  " * indent
        print(f"{indent_str}Task: {title}", file=sys.stderr)
        if labels:
            print(f"{indent_str}  Labels: {', '.join(labels)}", file=sys.stderr)
        if parent_id:
            print(f"{indent_str}  Parent ID: {parent_id}", file=sys.stderr)

        # Create a mock task object with just an id
        class MockTask:
            def __init__(self):
                import random
                self.id = f"debug_{random.randint(1000, 9999)}"

        created_task = MockTask()
    else:
        # Normal mode: create task via API
        try:
            print(f"DEBUG: Creating task with params: {task_params}", file=sys.stderr)
            created_task = api.add_task(**task_params)
            print(f"DEBUG: Task created successfully: {created_task.id}", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: Failed to create task: {str(e)}", file=sys.stderr)
            print(f"ERROR: Task params were: {task_params}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise

    # Create subtasks if they exist (ListBlock returns a list of dicts)
    if task_block.get('subtasks'):
        for subtask_data in task_block['subtasks']:
            # Subtasks are plain dicts from ListBlock
            create_task_recursive(api, subtask_data, token_values, parent_id=created_task.id, debug=debug, indent=indent+1)

    return created_task
