from django.db import models
from projects.models import Project

class Perspective(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    projects = models.ManyToManyField(
        Project,
        related_name='perspective',
        blank=True,
        db_table='perspective_perspective_projects'  # Nome explícito
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'perspective_perspective'  # Nome explícito para a tabela principal

    def __str__(self):
        return self.name