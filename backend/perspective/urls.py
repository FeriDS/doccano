from django.urls import path
from .views import PerspectiveList, PerspectiveDetail, ProjectsWithoutPerspectives

urlpatterns = [
    path("projects/<int:project_id>/perspectives", PerspectiveList.as_view(), name="perspective_list"),
    path("projects/<int:project_id>/perspectives/<int:perspective_id>", PerspectiveDetail.as_view(), name="perspective_detail"),
    path("projects/without-perspectives", ProjectsWithoutPerspectives.as_view(), name="projects_without_perspectives"),
]

