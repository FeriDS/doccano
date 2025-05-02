from django.urls import path
from .views import HistoricalAnnotationReportView, HistoricalReportListView, pdf_teste

urlpatterns = [
    path("historical-report/<int:project_id>/", HistoricalAnnotationReportView.as_view(), name="historical-report"),
    path("historical-report/list/<int:project_id>/", HistoricalReportListView.as_view(), name="historical-report-list"),
    path("teste-pdf/", pdf_teste),
]
