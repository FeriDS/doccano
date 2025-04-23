from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()

class AnnotationRule(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='annotation_rules')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class VotingConfig(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='voting_configs')
    name = models.CharField(max_length=255)
    description = models.TextField()
    voting_type = models.CharField(max_length=50, choices=[
        ('majority', 'Maioria simples'),
        ('consensus', 'Consenso total'),
        ('weighted', 'Ponderado por experiência'),
    ])
    min_votes = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name