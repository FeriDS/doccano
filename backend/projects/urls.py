from django.urls import path

from .views.member import MemberDetail, MemberList, MyRole
from .views.project import CloneProject, ProjectDetail, ProjectList
from .views.tag import TagDetail, TagList
from .views.perspective import (
    ProjectPerspectiveView,
    PerspectiveFieldListView,
    PerspectiveFieldDetailView,
    UserPerspectiveView,
    CheckPerspectiveCompletionView,
)

urlpatterns = [
    path(route="projects", view=ProjectList.as_view(), name="project_list"),
    path(route="projects/<int:project_id>", view=ProjectDetail.as_view(), name="project_detail"),
    path(route="projects/<int:project_id>/my-role", view=MyRole.as_view(), name="my_role"),
    path(route="projects/<int:project_id>/tags", view=TagList.as_view(), name="tag_list"),
    path(route="projects/<int:project_id>/tags/<int:tag_id>", view=TagDetail.as_view(), name="tag_detail"),
    path(route="projects/<int:project_id>/members", view=MemberList.as_view(), name="member_list"),
    path(route="projects/<int:project_id>/clone", view=CloneProject.as_view(), name="clone_project"),
    path(route="projects/<int:project_id>/members/<int:member_id>", view=MemberDetail.as_view(), name="member_detail"),
    
    # Perspective URLs
    path(
        route="projects/<int:project_id>/perspective",
        view=ProjectPerspectiveView.as_view(),
        name="project_perspective"
    ),
    path(
        route="projects/<int:project_id>/perspective/fields",
        view=PerspectiveFieldListView.as_view(),
        name="perspective_field_list"
    ),
    path(
        route="projects/<int:project_id>/perspective/fields/<int:field_id>",
        view=PerspectiveFieldDetailView.as_view(),
        name="perspective_field_detail"
    ),
    path(
        route="projects/<int:project_id>/perspective/my-answers",
        view=UserPerspectiveView.as_view(),
        name="user_perspective"
    ),
    path(
        route="projects/<int:project_id>/perspective/check-completion",
        view=CheckPerspectiveCompletionView.as_view(),
        name="check_perspective_completion"
    ),
]
