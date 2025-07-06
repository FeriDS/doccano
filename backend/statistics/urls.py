from django.urls import path

from .views import AnnotationStatisticsAPI, LabelDistributionAPI, ExportStatisticsAPI

urlpatterns = [
    path("annotations", AnnotationStatisticsAPI.as_view(), name="annotation_statistics"),
    path("discrepancies/<int:example_id>/distribution", LabelDistributionAPI.as_view(), name="label_distribution"),
    path("export/csv", ExportStatisticsAPI.as_view(), name="export_statistics_csv"),
    path("export/pdf", ExportStatisticsAPI.as_view(), name="export_statistics_pdf"),
    path("export/xlsx", ExportStatisticsAPI.as_view(), name="export_statistics_xlsx"),
] 