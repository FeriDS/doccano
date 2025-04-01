from django.db import models


class PerspectiveType(models.TextChoices):
    STRING = 'string', 'String'
    INTEGER = 'integer', 'Integer'
    BOOLEAN = 'boolean', 'Boolean'


class Perspective(models.Model):
    name = models.TextField(default="")
    type = models.CharField(max_length=10, choices=PerspectiveType.choices, default=PerspectiveType.STRING)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="perspectives")

    def __str__(self):
        return f"{self.name} ({self.type})"


class PerspectiveFieldType(models.TextChoices):
    STRING = 'string', 'String'
    INTEGER = 'integer', 'Integer'
    BOOLEAN = 'boolean', 'Boolean'
    CHOICE = 'choice', 'Choice'


class PerspectiveField(models.Model):
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name="fields")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=PerspectiveFieldType.choices)
    options = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.type})"
