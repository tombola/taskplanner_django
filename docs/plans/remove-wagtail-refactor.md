# Plan: Remove Wagtail, use django-jsonform + django-polymorphic + django-neapolitan

## Context

Remove Wagtail CMS dependency entirely from both `todosync_django` (reusable package) and `taskplanner_django` (Django project). Replace with:
- **django-jsonform** — JSON Schema-based form widget for editing nested task data (replaces Wagtail StreamField)
- **django-polymorphic** — automatic subclass resolution on querysets (replaces Wagtail `.specific`)
- **django-neapolitan** — CRUD views for TaskGroupTemplate (replaces Wagtail admin pages)

DB can be deleted; no migration continuity needed.

---

## Files to modify/create/delete

### todosync_django/src/todosync/

| File | Action | Summary |
|------|--------|---------|
| `models.py` | **Rewrite** | Remove Wagtail/modelcluster imports. BaseTaskGroupTemplate → PolymorphicModel. StreamField → django-jsonform JSONField. TaskSyncSettings → singleton Model. LabelActionRule → regular ForeignKey. |
| `blocks.py` | **Delete** | No longer needed — task schema defined inline on model |
| `forms.py` | **Edit** | Remove `.live()`, `.specific` calls |
| `views.py` | **Edit** | Remove Wagtail Site handling, remove `.specific` |
| `todoist_api.py` | **Edit** | Remove `site` param. Change StreamField iteration to plain list iteration. |
| `admin.py` | **Edit** | Add TaskSyncSettings + LabelActionRule inline to Django admin |
| `urls.py` | No change | |
| `apps.py` | No change | |
| `schemas.py` | No change | |
| `utils.py` | No change | |
| `management/commands/*.py` | **Edit** | Update help text (remove "Wagtail Admin" references) |
| `templates/todosync/base.html` | No change | |
| `templates/todosync/base_task_group_template.html` | **Delete** | Wagtail page template, no longer used |
| `templates/todosync/create_task_group.html` | **Edit** | Change task iteration from StreamField blocks to plain dicts |
| `tests/test_todoist_api.py` | **Edit** | Remove Wagtail imports (this is a debug script) |

### taskplanner_django/tasks/

| File | Action | Summary |
|------|--------|---------|
| `models.py` | **Edit** | Keep CropTask, BiennialCropTask, CropTaskGroupTemplate. No Wagtail code to remove. |
| `views.py` | **Rewrite** | Add neapolitan CRUDView for TaskGroupTemplate. Update home view. |
| `urls.py` | **Rewrite** | Mount neapolitan CRUD URLs at `admin/taskgrouptemplates/` |
| `admin.py` | **Edit** | Keep CropTask admin. Optionally add polymorphic admin for TaskGroupTemplate. |
| `wagtail_hooks.py` | **Delete** | Wagtail snippets, no longer used |

### taskplanner_django/taskplanner/

| File | Action | Summary |
|------|--------|---------|
| `settings/base.py` | **Edit** | Swap INSTALLED_APPS, remove Wagtail middleware/context_processors |
| `settings/dev.py` | **Edit** | Remove WAGTAILADMIN_BASE_URL |
| `settings/test.py` | **Edit** | Remove WAGTAILADMIN_BASE_URL |
| `urls.py` | **Rewrite** | Remove Wagtail URLs, add neapolitan URLs, move Django admin to /admin/ |

### taskplanner_django/templates/

| File | Action | Summary |
|------|--------|---------|
| `base.html` | **Edit** | Update admin link |
| `home.html` | **Edit** | Remove Wagtail `.url`, use `{% url %}` |

### pyproject.toml (both projects)

| File | Action | Summary |
|------|--------|---------|
| `todosync_django/pyproject.toml` | **Edit** | Remove wagtail, django-modelcluster. Add django-jsonform, django-polymorphic. |
| `taskplanner_django/pyproject.toml` | **Edit** | Remove wagtail. Add django-jsonform, django-polymorphic, neapolitan. |

---

## Detailed changes

### 1. todosync/models.py

**Remove imports:**
```python
# DELETE these
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, HelpPanel, InlinePanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from .blocks import TaskBlock
```

**Add imports:**
```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django_jsonform.models.fields import JSONField
from polymorphic.models import PolymorphicModel
```

**LabelActionRule** — change `ParentalKey` → `ForeignKey`, remove `panels`:
```python
class LabelActionRule(models.Model):
    settings = models.ForeignKey(
        'TaskSyncSettings',
        on_delete=models.CASCADE,
        related_name='label_action_rules'
    )
    # ... keep other fields unchanged, remove panels list
```

**TaskSyncSettings** — convert to singleton Django model:
```python
class TaskSyncSettings(models.Model):
    """Site-wide settings for task sync. Only one instance should exist."""
    default_project_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Default project ID for task sync."
    )

    class Meta:
        verbose_name = 'Task Sync Settings'
        verbose_name_plural = 'Task Sync Settings'

    def __str__(self):
        return "Task Sync Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton: always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

**BaseTaskGroupTemplate** — convert from Page to PolymorphicModel:
```python
TASKS_SCHEMA = {
    'type': 'array',
    'title': 'Tasks',
    'items': {
        'type': 'object',
        'title': 'Task',
        'properties': {
            'title': {
                'type': 'string',
                'title': 'Task title (can use tokens like {SKU})',
            },
            'labels': {
                'type': 'string',
                'title': 'Labels (comma-separated)',
            },
            'subtasks': {
                'type': 'array',
                'title': 'Subtasks',
                'items': {
                    'type': 'object',
                    'title': 'Subtask',
                    'properties': {
                        'title': {
                            'type': 'string',
                            'title': 'Subtask title (can use tokens)',
                        },
                        'labels': {
                            'type': 'string',
                            'title': 'Labels (comma-separated)',
                        },
                    },
                    'required': ['title'],
                },
            },
        },
        'required': ['title'],
    },
}


class BaseTaskGroupTemplate(PolymorphicModel):
    title = models.CharField(max_length=255)
    project_id = models.CharField(max_length=100, blank=True, help_text="...")
    description = models.TextField(blank=True, help_text="...")
    tasks = JSONField(schema=TASKS_SCHEMA, blank=True, default=list)

    class Meta:
        verbose_name = 'Task Group Template'
        verbose_name_plural = 'Task Group Templates'

    def __str__(self):
        return self.title

    def get_effective_project_id(self):
        if self.project_id:
            return self.project_id
        settings = TaskSyncSettings.load()
        return settings.default_project_id

    def get_parent_task_model(self):
        return self.parent_task_class

    def get_token_field_names(self):
        model = self.get_parent_task_model()
        if model:
            return model.get_token_field_names()
        return []
```

**Task** — no changes.

**BaseParentTask** — no changes.

### 2. Delete todosync/blocks.py

Entire file removed. Task structure defined via `TASKS_SCHEMA` dict in models.py.

### 3. todosync/forms.py

- Replace `BaseTaskGroupTemplate.objects.live()` → `.objects.all()`
- Remove `.specific` (django-polymorphic handles this automatically)
- Remove `site` kwarg handling

### 4. todosync/views.py

- Remove `from wagtail.models import Site` import
- Remove site resolution logic
- Remove `.specific` calls
- Change `create_tasks_from_template(api, template, token_values, site, ...)` → `create_tasks_from_template(api, template, token_values, ...)`

### 5. todosync/todoist_api.py

**`create_tasks_from_template`**: Remove `site` parameter. Change:
```python
# Before:
project_id = template.get_effective_project_id(site)

# After:
project_id = template.get_effective_project_id()
```

**Task iteration** — change StreamField format to plain JSON list:
```python
# Before:
for task_data in template.tasks:
    if task_data.block_type == 'task':
        task_block = task_data.value
        task_count += _create_task_recursive(api, task_block, ...)

# After:
for task_block in (template.tasks or []):
    task_count += _create_task_recursive(api, task_block, ...)
```

`_create_task_recursive` stays the same — it already expects a dict with `title`, `labels`, `subtasks` keys.

### 6. todosync/admin.py

Add TaskSyncSettings + LabelActionRule to Django admin:
```python
from .models import TaskSyncSettings, LabelActionRule

class LabelActionRuleInline(admin.TabularInline):
    model = LabelActionRule
    extra = 1

@admin.register(TaskSyncSettings)
class TaskSyncSettingsAdmin(admin.ModelAdmin):
    inlines = [LabelActionRuleInline]

    def has_add_permission(self, request):
        return not TaskSyncSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
```

### 7. tasks/views.py — neapolitan CRUDView

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from neapolitan.views import CRUDView

from .models import CropTaskGroupTemplate
from todosync.models import BaseTaskGroupTemplate


class TaskGroupTemplateCRUDView(LoginRequiredMixin, CRUDView):
    model = CropTaskGroupTemplate
    fields = ["title", "description", "project_id", "tasks"]
    # url_base set via neapolitan auto or manually routed


def home(request):
    templates = BaseTaskGroupTemplate.objects.all()
    return render(request, 'home.html', {'templates': templates})
```

### 8. taskplanner/urls.py

```python
from django.contrib import admin
from django.urls import include, path
from neapolitan.views import Role
from tasks.views import TaskGroupTemplateCRUDView, home

urlpatterns = [
    # Neapolitan CRUD (before Django admin catch-all)
    path('admin/taskgrouptemplates/', TaskGroupTemplateCRUDView.as_view(role=Role.LIST), name='taskgrouptemplate-list'),
    path('admin/taskgrouptemplates/new/', TaskGroupTemplateCRUDView.as_view(role=Role.CREATE), name='taskgrouptemplate-create'),
    path('admin/taskgrouptemplates/<int:pk>/', TaskGroupTemplateCRUDView.as_view(role=Role.DETAIL), name='taskgrouptemplate-detail'),
    path('admin/taskgrouptemplates/<int:pk>/edit/', TaskGroupTemplateCRUDView.as_view(role=Role.UPDATE), name='taskgrouptemplate-update'),
    path('admin/taskgrouptemplates/<int:pk>/delete/', TaskGroupTemplateCRUDView.as_view(role=Role.DELETE), name='taskgrouptemplate-delete'),
    # Django admin
    path('admin/', admin.site.urls),
    # Todosync (webhook + create form)
    path('todosync/', include('todosync.urls')),
    # Home
    path('', home, name='home'),
]
```

### 9. settings/base.py

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "django_jsonform",
    "polymorphic",
    "neapolitan",
    # Todosync package
    "todosync",
    # Local apps
    "tasks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Remove wagtail.contrib.settings.context_processors.settings from TEMPLATES
# Remove WAGTAIL_SITE_NAME
```

### 10. pyproject.toml changes

**todosync_django/pyproject.toml** — remove `wagtail>=6.0`, `django-modelcluster>=6.0`. Add `django-jsonform>=2.22.0`, `django-polymorphic>=4.0`.

**taskplanner_django/pyproject.toml** — remove `wagtail>=7.2`. Add `django-jsonform>=2.22.0`, `django-polymorphic>=4.0`, `neapolitan>=0.1`.

### 11. Templates

**`home.html`** — change `{{ template.url }}` to `{% url 'taskgrouptemplate-detail' template.pk %}`.

**`todosync/create_task_group.html`** — change StreamField iteration:
```html
<!-- Before -->
{% for block in selected_template.tasks %}
    {% if block.block_type == 'task' %}
    <li><strong>{{ block.value.title }}</strong>
        {% for subtask in block.value.subtasks %}...{% endfor %}
    </li>
    {% endif %}
{% endfor %}

<!-- After -->
{% for task in selected_template.tasks %}
    <li><strong>{{ task.title }}</strong>
        {% for subtask in task.subtasks %}...{% endfor %}
    </li>
{% endfor %}
```

**Delete** `todosync/base_task_group_template.html` (Wagtail page template).

### 12. Delete wagtail_hooks.py

Remove `taskplanner_django/tasks/wagtail_hooks.py` entirely.

### 13. Management commands

Update help text in `list_todoist_projects.py` and `list_todoist_sections.py` — change "Wagtail Admin → Settings" to "Django Admin → Task Sync Settings".

### 14. Test files

`test_todoist_api.py` — update/remove Wagtail imports (debug script). `test_webhook.py` — no changes needed (already uses plain Task model).

---

## Verification

1. **Install deps**: `cd taskplanner_django && uv sync`
2. **Delete old DB**: `rm db.sqlite3`
3. **Make migrations**: `uv run python manage.py makemigrations todosync tasks`
4. **Migrate**: `uv run python manage.py migrate`
5. **Create superuser**: `uv run python manage.py createsuperuser`
6. **Run server**: `uv run python manage.py runserver`
7. **Test Django admin**: Visit `/admin/` — verify TaskSyncSettings, Task, CropTask visible
8. **Test neapolitan CRUD**: Visit `/admin/taskgrouptemplates/` — verify list/create/edit/delete
9. **Test task creation**: Visit `/todosync/create/` — select template, fill tokens, submit
10. **Run tests**: `uv run pytest` — verify webhook tests still pass
