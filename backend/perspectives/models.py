from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

class PerspectiveField(models.Model):
    """Model to define fields that compose a perspective."""
    name = models.CharField(max_length=100)
    description = models.TextField(help_text="Description of what this field represents")
    field_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('number', 'Number'),
            ('boolean', 'Yes/No'),
            ('choice', 'Single Choice'),
            ('multiple', 'Multiple Choice')
        ],
        default='text'
    )
    choices = models.JSONField(
        null=True, 
        blank=True,
        help_text="Options for choice fields in JSON format. Example: ['option1', 'option2']"
    )
    required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Perspective(models.Model):
    """Model for defining a reusable perspective template."""
    name = models.CharField(max_length=100)
    description = models.TextField(help_text="Description of this perspective")
    fields = models.ManyToManyField(PerspectiveField, related_name='perspectives')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_perspectives')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ProjectPerspective(models.Model):
    """Model to associate a project with a perspective configuration."""
    project = models.OneToOneField(
        Project, 
        on_delete=models.CASCADE, 
        related_name='perspective_config'
    )
    perspective = models.ForeignKey(
        Perspective, 
        on_delete=models.PROTECT,  # Prevent deletion of perspective if it's being used
        related_name='project_perspectives'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.perspective.name}"

class UserPerspectiveAnswer(models.Model):
    """Model to store user responses for project perspectives."""
    project_perspective = models.ForeignKey(
        ProjectPerspective,
        on_delete=models.CASCADE,
        related_name='user_answers'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='perspective_answers'
    )
    field_values = models.JSONField(
        default=dict,
        help_text="Stores the values for each perspective field in JSON format"
    )
    is_complete = models.BooleanField(
        default=False,
        help_text="Indicates if all required fields have been filled"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project_perspective', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.project_perspective}"

    def validate_field_values(self):
        """Validates if all required fields have values."""
        required_fields = self.project_perspective.perspective.fields.filter(required=True).values_list('name', flat=True)
        # return all(field in self.field_values for field in required_fields)
        return all(field in self.field_values and self.field_values[field] not in [None, ''] for field in required_fields)

    def save(self, *args, **kwargs):
        self.is_complete = self.validate_field_values()
        super().save(*args, **kwargs)
