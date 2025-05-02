from django.urls import path, include
from perspective.views import PerspectiveList, PerspectiveDetail, ProjectsWithoutPerspectives

from .views import TaskStatus

urlpatterns = [
    path(route="tasks/status/<task_id>", view=TaskStatus.as_view(), name="task_status"),
    path("api/", include("perspective.urls")),
    path("projects/<int:project_id>/perspectives", PerspectiveList.as_view(), name="perspective_list"),
    path("projects/<int:project_id>/perspectives/<int:perspective_id>", PerspectiveDetail.as_view(), name="perspective_detail"),
    path("projects/without-perspectives", ProjectsWithoutPerspectives.as_view(), name="projects_without_perspectives"),
    path("reports/", include("backend.reports.urls")),

]
