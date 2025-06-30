from django.urls import path

from .views import AnnotationStatisticsAPI, LabelDistributionAPI

urlpatterns = [
    path("annotations", AnnotationStatisticsAPI.as_view(), name="annotation_statistics"),
    path("discrepancies/<int:example_id>/distribution", LabelDistributionAPI.as_view(), name="label_distribution"),
] 