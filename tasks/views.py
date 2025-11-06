from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from todoist_api_python.api import TodoistAPI
from .models import TaskGroupTemplate
from .forms import TaskGroupCreationForm


def create_task_group(request):
    """View for creating task groups from templates"""

    template_id = request.GET.get('template_id') or request.POST.get('template_id')

    if request.method == 'POST':
        form = TaskGroupCreationForm(request.POST, template_id=template_id)

        if form.is_valid():
            template = form.cleaned_data['task_group_template']
            token_values = form.get_token_values()

            # Create tasks via Todoist API
            try:
                api_token = getattr(settings, 'TODOIST_API_TOKEN', None)
                if not api_token:
                    messages.error(request, 'Todoist API token not configured')
                    return redirect('tasks:create_task_group')

                api = TodoistAPI(api_token)
                created_tasks = create_tasks_from_template(api, template, token_values)

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


def create_tasks_from_template(api, template, token_values):
    """Create Todoist tasks from template with token substitution"""
    created_tasks = []

    for task_data in template.tasks:
        if task_data.block_type == 'task':
            task_block = task_data.value
            created_task = create_task_recursive(api, task_block, token_values)
            if created_task:
                created_tasks.append(created_task)

    return created_tasks


def create_task_recursive(api, task_block, token_values, parent_id=None):
    """Recursively create a task and its subtasks"""

    # Substitute tokens in title
    title = task_block['title']
    for token, value in token_values.items():
        title = title.replace(f'{{{token}}}', value)

    # Parse labels
    labels = []
    if task_block.get('labels'):
        labels = [label.strip() for label in task_block['labels'].split(',') if label.strip()]

    # Create task via API
    task_params = {
        'content': title,
        'labels': labels,
    }

    if parent_id:
        task_params['parent_id'] = parent_id

    created_task = api.add_task(**task_params)

    # Create subtasks if they exist
    if task_block.get('subtasks'):
        for subtask_data in task_block['subtasks']:
            if subtask_data.block_type == 'task':
                create_task_recursive(api, subtask_data.value, token_values, parent_id=created_task.id)

    return created_task
