from django.urls import path  # Adicione esta linha
from .views import ProjectRuleListView, RuleVoteView, ProjectRuleUpdateView, ProjectRuleAPIView

urlpatterns = [
    path("projects/<int:project_id>/rules/", ProjectRuleListView.as_view(), name="project-rule-list"),
    path("projects/<int:project_id>/rules/<int:rule_id>/vote/", RuleVoteView.as_view(), name="project-rule-vote"),
    path("projects/<int:project_id>/rules/<int:rule_id>/", ProjectRuleUpdateView.as_view(), name="project-rule-update"),
    path(
    "projects/<int:project_id>/rules/",
    ProjectRuleAPIView.as_view(),
    name="project-rule-api",
),
]