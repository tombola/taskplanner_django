from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from neapolitan.views import CRUDView

from todosync.models import BaseTaskGroupTemplate

from .models import CropTaskGroupTemplate


class TaskGroupTemplateCRUDView(LoginRequiredMixin, CRUDView):
    model = CropTaskGroupTemplate
    fields = ["title", "description", "project_id", "tasks"]


def home(request):
    templates = BaseTaskGroupTemplate.objects.all()
    return render(request, "home.html", {"templates": templates})
