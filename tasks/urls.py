from django.urls import path, include

app_name = 'tasks'

urlpatterns = [
    # Include todosync URLs
    path('', include('todosync.urls')),
]
