from django.urls import path
from .views import DiscrepancyCreateView, ListExamplesWithAnnotationsView

urlpatterns = [
    path('projects/<int:project_id>/discrepancies/annotations/', ListExamplesWithAnnotationsView.as_view()),
    path('projects/<int:project_id>/discrepancies/examples/<int:example_id>/', DiscrepancyCreateView.as_view()),
]
