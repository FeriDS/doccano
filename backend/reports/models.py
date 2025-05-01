# backend/reports/models.py
from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()

class AnnotationReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    filters = models.JSONField()
    csv_file = models.FileField(upload_to='reports/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"Relatório de {self.project.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
