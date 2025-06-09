from django.db import models
from django.contrib.auth.models import User
from projects.models import Project

class AnnotationPerspective(models.Model):
    """Model to store annotator perspectives and contexts."""
    name = models.CharField(max_length=100)
    description = models.TextField(help_text="Detailed description of the annotator's perspective or context")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_perspectives')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='annotation_perspectives')
    
    class Meta:
        unique_together = ('name', 'project')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.project.name}" 