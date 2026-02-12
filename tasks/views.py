from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from neapolitan.views import CRUDView

from todosync.models import BaseParentTask, BaseTaskGroupTemplate, Task

from .models import CropTaskGroupTemplate


class TaskGroupTemplateCRUDView(LoginRequiredMixin, CRUDView):
    model = CropTaskGroupTemplate
    fields = ["title", "description", "project_id", "tasks"]
    url_base = "taskgrouptemplate"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_task_class = self.model.parent_task_class
        if parent_task_class:
            context["token_names"] = parent_task_class.get_token_field_names()
        return context


def home(request):
    templates = BaseTaskGroupTemplate.objects.all()

    now = timezone.now()
    month_start = now.date().replace(day=1)
    if now.month == 12:
        month_end = month_start.replace(year=now.year + 1, month=1)
    else:
        month_end = month_start.replace(month=now.month + 1)

    total_tasks = Task.objects.count()

    due_this_month = Task.objects.filter(
        Q(start_date__gte=month_start, start_date__lt=month_end) | Q(due_date__gte=month_start, due_date__lt=month_end)
    ).distinct()
    due_this_month_count = due_this_month.count()
    due_this_month_completed = due_this_month.filter(completed=True).count()
    if due_this_month_count > 0:
        completion_pct = round(due_this_month_completed / due_this_month_count * 100)
    else:
        completion_pct = None

    return render(
        request,
        "home.html",
        {
            "templates": templates,
            "total_tasks": total_tasks,
            "due_this_month_count": due_this_month_count,
            "due_this_month_completed": due_this_month_completed,
            "completion_pct": completion_pct,
            "current_month": now.strftime("%B %Y"),
        },
    )


def template_list(request):
    templates = BaseTaskGroupTemplate.objects.all()
    return render(request, "template_list.html", {"templates": templates})


def template_tasks(request, pk):
    template = get_object_or_404(BaseTaskGroupTemplate, pk=pk)
    parent_task_model = template.get_parent_task_model() or BaseParentTask
    parent_tasks = (
        parent_task_model.objects.filter(template=template).select_related("template").prefetch_related("subtasks")
    )
    return render(
        request,
        "template_tasks.html",
        {"template": template, "parent_tasks": parent_tasks},
    )
