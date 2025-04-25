from django.urls import path
from .views import ProjectRuleListView, RuleVoteView, ProjectRuleUpdateView

urlpatterns = [
    path("projects/<int:project_id>/rules/", ProjectRuleListView.as_view(), name="project-rule-list"),
    path("projects/<int:project_id>/rules/<int:rule_id>/vote/", RuleVoteView.as_view(), name="project-rule-vote"),
    path("projects/<int:project_id>/rules/<int:rule_id>/", ProjectRuleUpdateView.as_view(), name="project-rule-update"),  # <- este
]
