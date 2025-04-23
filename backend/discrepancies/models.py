from django.db import models
from django.conf import settings
from examples.models import Example
from projects.models import Project

class Discrepancy(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    example = models.ForeignKey(Example, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'example')