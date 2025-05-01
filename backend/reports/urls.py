from django.urls import path
from .views import AnnotationReportView, AnnotationReportDataView

urlpatterns = [
    path('annotations/', AnnotationReportView.as_view(), name='annotation-report'),
    path('annotations/<int:pk>/data/', AnnotationReportDataView.as_view(), name='annotation-report-data'),
]
