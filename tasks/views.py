from django.shortcuts import render
from todosync.models import BaseTaskGroupTemplate


def home(request):
    templates = BaseTaskGroupTemplate.objects.live().specific()
    return render(request, 'home.html', {'templates': templates})
