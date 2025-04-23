from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()

class PerspectiveField(models.Model):
    FIELD_TYPES = [
        ('int', 'Número inteiro'),
        ('string', 'Texto'),
        ('bool', 'Booleano'),
    ]
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=10, choices=FIELD_TYPES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"

class Perspective(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    fields = models.ManyToManyField(PerspectiveField, related_name='perspectives')

    def __str__(self):
        return self.name
    
class ProjectPerspective(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='project_perspective')
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)

    def __str__(self):
        return f"Perspetiva do Projeto: {self.project.name}"
    
class UserPerspectiveAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    field = models.ForeignKey(PerspectiveField, on_delete=models.CASCADE)

    value_string = models.TextField(null=True, blank=True)
    value_int = models.IntegerField(null=True, blank=True)
    value_bool = models.BooleanField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'project', 'field')
        verbose_name = "Resposta de Perspetiva do Utilizador"
        verbose_name_plural = "Respostas de Perspetiva dos Utilizadores"

    def get_value(self):
        if self.field.field_type == 'string':
            return self.value_string
        elif self.field.field_type == 'int':
            return self.value_int
        elif self.field.field_type == 'bool':
            return self.value_bool
        return None  # segurança adicional caso tipo seja inválido
    
    def __str__(self):
        return f"{self.user.username} @ {self.project.name} → {self.field.name}: {self.get_value()}"