from rest_framework import serializers
from .models import Perspective
from projects.serializers import ProjectSerializer  # Importe o serializer de projetos

class PerspectiveSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)  # Mostra projetos completos
    # Ou se quiser apenas IDs:
    # project_ids = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     read_only=True,
    #     source='projects'
    # )
    
    class Meta:
        model = Perspective
        fields = ['id', 'name', 'description', 'projects', 'created_at']