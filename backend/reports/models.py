from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class HistoricalReport(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user_filter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='filtered_reports')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    total_annotations = models.IntegerField()
    total_users = models.IntegerField()
    rules_count = models.IntegerField()

    # ❗ A ForeignKey para Project fica aqui, mas definida *tardiamente* por string
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)

    def __str__(self):
        return f"Histórico de {self.project.name} em {self.created_at.date()}"
