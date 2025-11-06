from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks


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


class TaskGroupTemplate(Page):
    """Wagtail page type for task group templates"""

    tokens = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of tokens (e.g., SKU, VARIETYNAME)"
    )

    tasks = StreamField([
        ('task', TaskBlock()),
    ], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('tokens'),
        FieldPanel('tasks'),
    ]

    class Meta:
        verbose_name = 'Task Group Template'

    def get_token_list(self):
        """Return list of tokens from comma-separated string"""
        if not self.tokens:
            return []
        return [token.strip() for token in self.tokens.split(',') if token.strip()]
