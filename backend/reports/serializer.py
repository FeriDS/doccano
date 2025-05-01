from rest_framework import serializers
from .models import AnnotationReport

class AnnotationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationReport
        fields = ['id', 'project', 'created_by', 'created_at', 'filters']  # <- inclui 'id'!
