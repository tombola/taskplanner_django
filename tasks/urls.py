from django.urls import include, path

app_name = 'tasks'

urlpatterns = [
    # Include todosync URLs
    path('', include('todosync.urls')),
]
