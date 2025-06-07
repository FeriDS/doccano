from django.urls import path,include

from .views import TaskStatus

urlpatterns = [
    path(route="tasks/status/<task_id>", view=TaskStatus.as_view(), name="task_status"),
]