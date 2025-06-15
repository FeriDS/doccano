from django.urls import path

from .views import AnnotationStatisticsAPI

urlpatterns = [
    path("annotations", AnnotationStatisticsAPI.as_view(), name="annotation_statistics"),
] 