from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from neapolitan.views import CRUDView

from todosync.models import BaseTaskGroupTemplate

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
    return render(request, "home.html", {"templates": templates})
