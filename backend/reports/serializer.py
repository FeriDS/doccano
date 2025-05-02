# backend/reports/serializer.py

from rest_framework import serializers
from .models import HistoricalReport

class HistoricalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalReport
        fields = "__all__"
