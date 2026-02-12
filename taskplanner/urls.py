from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from neapolitan.views import Role

from tasks.views import TaskGroupTemplateCRUDView, home, template_list

urlpatterns = [
    # Neapolitan CRUD views (before Django admin catch-all)
    path("admin/taskgrouptemplates/", TaskGroupTemplateCRUDView.as_view(role=Role.LIST), name="taskgrouptemplate-list"),
    path(
        "admin/taskgrouptemplates/new/",
        TaskGroupTemplateCRUDView.as_view(role=Role.CREATE),
        name="taskgrouptemplate-create",
    ),
    path(
        "admin/taskgrouptemplates/<int:pk>/",
        TaskGroupTemplateCRUDView.as_view(role=Role.DETAIL),
        name="taskgrouptemplate-detail",
    ),
    path(
        "admin/taskgrouptemplates/<int:pk>/edit/",
        TaskGroupTemplateCRUDView.as_view(role=Role.UPDATE),
        name="taskgrouptemplate-update",
    ),
    path(
        "admin/taskgrouptemplates/<int:pk>/delete/",
        TaskGroupTemplateCRUDView.as_view(role=Role.DELETE),
        name="taskgrouptemplate-delete",
    ),
    # Django admin
    path("admin/", admin.site.urls),
    # Todosync (webhook + create form)
    path("todosync/", include("todosync.urls")),
    # Home
    path("", home, name="home"),
    path("templates/", template_list, name="template-list"),
]

if settings.DEBUG:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
