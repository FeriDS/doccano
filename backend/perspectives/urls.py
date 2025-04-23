from django.urls import path
from .views import GetProjectPerspectiveFields, SubmitUserPerspectiveAnswers

urlpatterns = [
    path('projects/<int:project_id>/perspective/fields/', GetProjectPerspectiveFields.as_view()),
    path('projects/<int:project_id>/perspective/answers/', SubmitUserPerspectiveAnswers.as_view()),
]
