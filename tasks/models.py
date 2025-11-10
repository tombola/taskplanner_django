from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


class TaskBlock(blocks.StructBlock):
    """Block for a single task with title and labels"""
    title = blocks.CharBlock(required=True, help_text="Task title (can use tokens like {SKU})")
    labels = blocks.CharBlock(required=False, help_text="Comma-separated labels (e.g., sow, plant)")
    subtasks = blocks.ListBlock(
        blocks.StructBlock([
            ('title', blocks.CharBlock(required=True, help_text="Subtask title (can use tokens)")),
            ('labels', blocks.CharBlock(required=False, help_text="Comma-separated labels")),
        ]),
        required=False,
        help_text="Subtasks for this task"
    )

    class Meta:
        icon = 'task'
        label = 'Task'


@register_setting
class TaskPlannerSettings(BaseSiteSetting):
    """Site-wide settings for task planner"""

    tokens = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of tokens (e.g., SKU, VARIETYNAME)"
    )

    parent_task_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Title template for parent task (can use tokens like {SKU}). If empty, uses the template page title."
    )

    panels = [
        FieldPanel('tokens'),
        FieldPanel('parent_task_title'),
    ]

    class Meta:
        verbose_name = 'Task Planner Settings'

    def get_token_list(self):
        """Return list of tokens from comma-separated string"""
        if not self.tokens:
            return []
        return [token.strip() for token in self.tokens.split(',') if token.strip()]


class TaskGroupTemplate(Page):
    """Wagtail page type for task group templates"""

    tasks = StreamField([
        ('task', TaskBlock()),
    ], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('tasks'),
    ]

    template = 'tasks/task_group_template.html'

    class Meta:
        verbose_name = 'Task Group Template'


